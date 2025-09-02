"""BUCKEYE RL - Commands for reinforcement learning with Buckeye environments."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003

import typer

from buckeyelabs.utils.design import BUCKDesign

# Create the RL subcommand app
rl_app = typer.Typer(
    name="rl",
    help="🤖 Reinforcement learning commands for Buckeye environments",
    rich_markup_mode="rich",
)

design = BUCKDesign()


@rl_app.callback(invoke_without_command=True)
def rl_main(
    ctx: typer.Context,
    model: str = typer.Option("Qwen/Qwen2.5-3B-Instruct", "--model", "-m", help="Model to train"),
    dataset: str | None = typer.Option(
        None, "--dataset", "-d", help="Override dataset from lock file"
    ),
    config: Path | None = typer.Option(None, "--config", "-c", help="Config YAML path"),  # noqa: B008
    gpus: str = typer.Option("2xA100", "--gpus", help="GPU configuration (e.g., 2xA100, 4xH100)"),
    provider: str = typer.Option("prime", "--provider", help="Infrastructure provider"),
    output_dir: Path = typer.Option("./checkpoints", "--output", "-o", help="Output directory"),  # noqa: B008
) -> None:
    """🤖 Train RL models on Buckeye environments.

    Runs training on remote GPU infrastructure with automatic setup.
    The command will:
    1. Check for required files (config, dataset)
    2. Offer to generate missing files
    3. Push environment to registry if needed
    4. Start remote training on Prime Intellect

    Examples:
        buckeye rl                    # Interactive mode with prompts
        buckeye rl --model gpt2       # Train with specific model
        buckeye rl --gpus 4xH100      # Use different GPU configuration
        buckeye rl init my-env:latest # Generate config for environment
    """
    # Only run main command if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        from .train import train_command_wrapper

        train_command_wrapper(
            model=model,
            dataset=dataset,
            config=config,
            gpus=gpus,
            provider=provider,
            output_dir=output_dir,
        )


@rl_app.command()
def init(
    directory: str = typer.Argument(".", help="Environment directory or Docker image"),
    output: Path = typer.Option(None, "--output", "-o", help="Output config file path"),  # noqa: B008
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
    build: bool = typer.Option(False, "--build", "-b", help="Build environment if no lock file"),
) -> None:
    """🔧 Generate buckeye-vf-gym config from environment.

    Generates a YAML configuration file compatible with the buckeye-vf-gym adapter
    from either a directory with buckeye.lock.yaml or a Docker image.

    Examples:
        buckeye rl init                    # Use current directory
        buckeye rl init environments/test  # Use specific directory
        buckeye rl init my-env:latest      # Use Docker image directly
        buckeye rl init . -o configs/2048.yaml --build
    """
    from .init import init_command_wrapper

    init_command_wrapper(directory, output, force, build)
