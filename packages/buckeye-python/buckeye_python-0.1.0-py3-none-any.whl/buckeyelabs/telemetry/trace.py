"""User-facing trace context manager for Buckeye telemetry.

This module provides the simple trace() API that users interact with.
The actual OpenTelemetry implementation is in buckeyelabs.otel.
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from buckeyelabs.otel import configure_telemetry
from buckeyelabs.otel import trace as OtelTrace

if TYPE_CHECKING:
    from collections.abc import Generator

__all__ = ["trace"]


@contextmanager
def trace(
    name: str = "Test task from buckeye",
    *,
    root: bool = True,
    attrs: dict[str, Any] | None = None,
    job_id: str | None = None,
    task_id: str | None = None,
) -> Generator[str, None, None]:
    """Start a Buckeye trace context.

    A unique task_run_id is automatically generated for each trace.

    Args:
        name: Descriptive name for this trace/task
        root: Whether this is a root trace (updates task status)
        attrs: Additional attributes to attach to the trace
        job_id: Optional job ID to associate with this trace

    Yields:
        str: The auto-generated task run ID

    Usage:
        import buckeyelabs

        with buckeyelabs.trace("My Task") as task_run_id:
            # Your code here
            print(f"Running task: {task_run_id}")

        # Or with default name:
        with buckeyelabs.trace() as task_run_id:
            pass

        # Or with job_id:
        with buckeyelabs.trace("My Task", job_id="550e8400-e29b-41d4-a716-446655440000") as task_run_id:
            pass
    """
    # Ensure telemetry is configured
    configure_telemetry()

    # Only generate task_run_id if using Buckeye backend
    # For custom OTLP backends, we don't need it
    from buckeyelabs.settings import get_settings

    settings = get_settings()

    if settings.telemetry_enabled and settings.api_key:
        task_run_id = str(uuid.uuid4())
    else:
        # Use a placeholder for custom backends
        task_run_id = "custom-otlp-trace"

    # Delegate to OpenTelemetry implementation
    with OtelTrace(
        task_run_id,
        is_root=root,
        span_name=name,
        attributes=attrs or {},
        job_id=job_id,
        task_id=task_id,
    ) as run_id:
        yield run_id
