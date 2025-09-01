from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class McpTool:
    """Represents an MCP tool with its name and permission settings."""

    name: str
    title: str
    description: Optional[str] = None
    required: Optional[list[str]] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    annotations: Optional[list[str]] = None
    meta: Optional[str] = None
    permission: str = "manual"  # "manual" or "auto"
