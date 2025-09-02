"""Standard asyncio-based dataset runner."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, cast

from datasets import Dataset, load_dataset

from buckeyelabs.agents.misc import ResponseAgent
from buckeyelabs.datasets.task import Task

if TYPE_CHECKING:
    from buckeyelabs.agents import MCPAgent

logger = logging.getLogger("buckeye.datasets")


async def run_dataset(
    name: str,
    dataset: str | Dataset | list[dict[str, Any]],
    agent_class: type[MCPAgent],
    agent_config: dict[str, Any] | None = None,
    max_concurrent: int = 50,
    metadata: dict[str, Any] | None = None,
    max_steps: int = 10,
    split: str = "train",
    auto_respond: bool = False,
    custom_system_prompt: str | None = None,
    remote: bool = True,
) -> list[Any]:
    """
    Run all tasks in a dataset with automatic job tracking.

    Args:
        name: Name for the job
        dataset: HuggingFace dataset identifier (e.g. "hud-evals/SheetBench-50"),
                Dataset object, OR list of Task objects
        agent_class: Agent class to instantiate (e.g., ClaudeAgent)
        agent_config: Configuration/kwargs for agent (model, etc.)
        max_concurrent: Maximum parallel task execution
        metadata: Optional metadata for the job
        max_steps: Maximum steps per task
        split: Dataset split to use when loading from string (default: "train")
        auto_respond: Whether to use auto-response agent
        custom_system_prompt: Override system prompt for all tasks
        remote: Whether to run the job remotely (default: True)

    Returns:
        List of results from agent.run() in dataset order

    Example:
        >>> from buckeyelabs.agents import ClaudeAgent
        >>> # Option 1: From dataset string identifier
        >>> results = await run_dataset(
        ...     "SheetBench Eval",
        ...     "hud-evals/SheetBench-50",
        ...     ClaudeAgent,
        ...     {"model": "claude-3-5-sonnet-20241022"},
        ... )
        >>> # Option 2: From HuggingFace dataset object
        >>> from datasets import load_dataset
        >>> dataset = load_dataset("hud-evals/SheetBench-50", split="train")
        >>> results = await run_dataset("my_eval", dataset, ClaudeAgent)
        >>> # Option 3: From list of dicts
        >>> tasks = [{"prompt": "...", "mcp_config": {...}, ...}, ...]
        >>> results = await run_dataset("browser_eval", tasks, ClaudeAgent)
    """
    # Import here to avoid circular imports
    import buckeyelabs
    from buckeyelabs.settings import settings

    dataset_link = None

    # Load dataset from string if needed
    if isinstance(dataset, str):
        logger.info("Loading dataset %s from HuggingFace...", dataset)
        dataset_link = dataset

        # Load dataset from HuggingFace
        dataset = cast("Dataset", load_dataset(dataset, split=split))

    # Create job context
    job_metadata = metadata or {}
    job_metadata["agent_class"] = agent_class.__name__
    job_metadata["agent_config"] = agent_config

    # Extract dataset verification info if available
    if isinstance(dataset, Dataset) and not dataset_link:
        try:
            general_info = next(iter(dataset.info.__dict__["download_checksums"].keys())).split("/")
            project = general_info[3]
            dataset_name = general_info[4].split("@")[0]
            dataset_link = f"{project}/{dataset_name}"
        except Exception:
            logger.warning("Failed to extract dataset verification info")

    job_context = (
        buckeyelabs.job(name, metadata=job_metadata, dataset_link=dataset_link)
        if remote
        else _dummy_job_context()
    )
    with job_context as job_obj:
        # Run tasks with semaphore for concurrency control
        sem = asyncio.Semaphore(max_concurrent)
        results: list[Any | None] = [None] * len(dataset)

        async def _worker(index: int, task_dict: Any, max_steps: int = 10) -> None:
            async with sem:
                # Create trace for this task
                task_name = task_dict.get("prompt") or f"Task {index}"
                if custom_system_prompt and "system_prompt" not in task_dict:
                    task_dict["system_prompt"] = custom_system_prompt
                with buckeyelabs.trace(
                    task_name,
                    job_id=job_obj.id,
                    task_id=task_dict.get("id"),
                    remote=bool(settings.api_key),
                ):
                    # Convert dict to Task here, at trace level
                    task = Task(**task_dict)

                    agent = agent_class(**(agent_config or {}))

                    if auto_respond:
                        agent.response_agent = ResponseAgent()
                    results[index] = await agent.run(task, max_steps=max_steps)

        # Execute all tasks
        await asyncio.gather(
            *[_worker(i, task, max_steps=max_steps) for i, task in enumerate(dataset)],
            return_exceptions=True,  # Don't fail entire batch on one error
        )

    return results


def _dummy_job_context():
    from contextlib import contextmanager

    @contextmanager
    def dummy_context():
        class DummyJob:
            id = None

        yield DummyJob()

    return dummy_context()
