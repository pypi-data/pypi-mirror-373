from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from buckeyelabs.settings import settings

logger = logging.getLogger(__name__)


class MCPConfigPatch(BaseModel):
    """Patch for MCP config."""

    headers: dict[str, Any] | None = Field(default_factory=dict, alias="headers")
    meta: dict[str, Any] | None = Field(default_factory=dict, alias="meta")


def patch_mcp_config(mcp_config: dict[str, dict[str, Any]], patch: MCPConfigPatch) -> None:
    """Patch MCP config with additional values."""
    buckeye_mcp_url = settings.buckeye_mcp_url

    for server_cfg in mcp_config.values():
        url = server_cfg.get("url", "")

        # 1) HTTP header lane (only for Buckeye MCP servers)
        if buckeye_mcp_url in url and patch.headers:
            for key, value in patch.headers.items():
                headers = server_cfg.setdefault("headers", {})
                headers.setdefault(key, value)

        # 2) Metadata lane (for all Buckeye MCP     servers)
        if patch.meta:
            for key, value in patch.meta.items():
                meta = server_cfg.setdefault("meta", {})
                meta.setdefault(key, value)


def setup_buckeye_telemetry(
    mcp_config: dict[str, dict[str, Any]], auto_trace: bool = True
) -> Any | None:
    """Setup telemetry for buckeye servers.

    Returns:
        The auto-created trace context manager if one was created, None otherwise.
        Caller is responsible for exiting the context manager.
    """
    if not mcp_config:
        raise ValueError("Please run initialize() before setting up client-side telemetry")

    # Check if there are any Buckeye servers to setup telemetry for
    buckeye_mcp_url = settings.buckeye_mcp_url
    has_buckeye_servers = any(
        buckeye_mcp_url in server_cfg.get("url", "") for server_cfg in mcp_config.values()
    )

    # If no Buckeye servers, no need for telemetry setup
    if not has_buckeye_servers:
        return None

    from buckeyelabs.otel import get_current_task_run_id
    from buckeyelabs.telemetry import trace

    run_id = get_current_task_run_id()
    auto_trace_cm = None

    if not run_id and auto_trace:
        auto_trace_cm = trace("My Trace")
        run_id = auto_trace_cm.__enter__()

    # Patch Buckeye servers with run-id (works whether auto or user trace)
    if run_id:
        patch_mcp_config(
            mcp_config,
            MCPConfigPatch(headers={"Run-Id": run_id}, meta={"run_id": run_id}),
        )

    return auto_trace_cm
