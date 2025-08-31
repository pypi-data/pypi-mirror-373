#!/usr/bin/env python

import json
import re
from typing import Dict, Optional, Tuple, Any


class McpToolParser:
    """Parser for MCP tool execution requests from LLM output."""

    # Regular expression pattern for extracting tool execution requests
    TOOL_PATTERN = re.compile(
        r"<use_mcp_tool>\s*"
        r"<server_name>(.*?)</server_name>\s*"
        r"<tool_name>(.*?)</tool_name>\s*"
        r"<arguments>\s*([\s\S]*?)\s*</arguments>\s*"
        r"</use_mcp_tool>",
        re.DOTALL,
    )

    @classmethod
    def extract_tool_requests(cls, text: str) -> list[Tuple[str, str, Dict[str, Any]]]:
        """
        Extract MCP tools execution request from text.

        Args:
            text: The text to parse for tool execution requests

        Returns:
            A list of (server_name, tool_name, arguments) if a request is found,
        """
        match = cls.TOOL_PATTERN.findall(text)

        return [
            (
                server_name.strip(),
                tool_name.strip(),
                McpToolParser.parse_arguments(arguments),
            )
            for server_name, tool_name, arguments in match
        ]

    @classmethod
    def parse_arguments(cls, arguments_str: str) -> Optional[Dict[str, Any]]:
        """
        Parse the arguments string into a dictionary.

        Args:
            arguments_str: The arguments string to parse
        """

        try:
            return json.loads(arguments_str.strip())
        except json.JSONDecodeError:
            # If JSON parsing fails, return None
            return None

    @classmethod
    def format_tool_result(cls, identifier: str, result: str) -> str:
        """
        Format the result of a tool execution for the LLM.

        Args:
            identifier: The identifier for the tool execution
            result: The result of the tool execution

        Returns:
            The formatted result
        """
        return f"""
MCP Tool execution result for {identifier}:
```
{result}
```
"""

    @classmethod
    def format_tool_error(cls, identifier: str, error: str) -> str:
        """
        Format an error message for the LLM.

        Args:
            identifier: The identifier for the tool execution
            error: The error message

        Returns:
            The formatted error message
        """
        return f"""
MCP Tool execution error for {identifier}:
```
{error}
```
"""

    @classmethod
    def _generate_example_args(cls, input_schema: Optional[Dict]) -> Dict:
        """Generate example arguments based on the input schema."""
        if not input_schema or "properties" not in input_schema:
            return {"param1": "value1", "param2": "value2"}

        example_args = {}
        type_mapping = {
            "string": lambda x: f"example_{x}",
            "number": lambda _: 42,
            "boolean": lambda _: True,
            "array": lambda _: [],
            "object": lambda _: {},
        }

        for prop_name, prop_info in input_schema["properties"].items():
            prop_type = prop_info.get("type", "string")
            example_args[prop_name] = type_mapping.get(prop_type, lambda _: "value")(
                prop_name
            )

        return example_args

    @classmethod
    def _format_schema(cls, schema_name: str, schema: Optional[Dict]) -> str:
        """Format schema as a markdown code block."""
        if not schema:
            return ""
        return (
            f"**{schema_name}:**\n```json\n"
            f"{json.dumps(schema, indent=2)}\n"
            "```\n\n"
        )

    @classmethod
    def format_available_tools(cls, tools_by_server: Dict[str, list]) -> str:
        """
        Format the available tools for inclusion in the system prompt.

        Args:
            tools_by_server: A dictionary mapping server names to lists of tools

        Returns:
            A formatted string describing the available tools
        """
        if not tools_by_server:
            return "No MCP tools available."

        result = ["# Available MCP Tools\n"]

        for server_name, tools in tools_by_server.items():
            result.append(f"## Server: {server_name}\n")

            for tool in tools:
                tool_sections = [
                    f"### {tool.name}\n",
                    f"{tool.description}\n\n" if tool.description else "",
                    f"**Permission:** {tool.permission}\n\n",
                    cls._format_schema("Input Schema", tool.input_schema),
                    cls._format_schema("Output Schema", tool.output_schema),
                    "**Usage Example:**\n",
                    "```xml\n",
                    f"<use_mcp_tool>\n  <server_name>{server_name}</server_name>\n  <tool_name>{tool.name}</tool_name>\n   <arguments>\n{json.dumps(cls._generate_example_args(tool.input_schema), indent=2)}\n   </arguments>\n</use_mcp_tool>\n",
                    "```\n\n",
                ]
                result.extend(tool_sections)

        return "".join(result)
