mcp_tool_shell_prompt = """
- **Important**: When solving tasks, always prioritize using shell commands (powershell/bash/zsh) when possible.
"""

mcp_tool_prompt = """
# MCP Tool Principles
{mcp_tool_shell_prompt}
- List **1–3 relevant MCP tools**.
- Write **complete, runnable tool calls** with **all parameters filled**.
- Use **structured Markdown** only.
- Enclose tool calls in correct triple backtick code blocks with language identifiers (e.g., ```xml```, ```json```).
- **Never** use placeholders or modify XML tag structure.
- Use **absolute paths** based on the current working directory.
- **Always** show execution results and **ask for user confirmation** before proceeding.

# MCP Tool Instructions
You can use Model Context Protocol (MCP) tools to connect with external systems.  
To invoke a tool, include a tool execution block using the exact format below:
```xml
<use_mcp_tool>
    <server_name>server name here</server_name>
    <tool_name>tool name here</tool_name>
    <arguments>
    {{
      "param1": "value1",
      "param2": "value2"
    }}
    </arguments>
</use_mcp_tool>
```
When **multiple** use_mcp_tool calls are required, wrap them inside **execute_mcp** for processing.
Even though you can return multiple items or results, **each use_mcp_tool call must always handle only a single tool call at a time.**
**Do not combine multiple tool calls into a single use_mcp_tool; instead, use execute_mcp to sequence them.**
```xml
<execute_mcp>
    <use_mcp_tool>
        <server_name>server name here</server_name>
        <tool_name>tool name here</tool_name>
        <arguments>
        {{
          "param1": "value1",
          "param2": "value2"
        }}
        </arguments>
    </use_mcp_tool>
    <use_mcp_tool>
        <server_name>server name here</server_name>
        <tool_name>tool name here</tool_name>
        <arguments>
        {{
          "param1": "value1",
          "param2": "value2"
        }}
        </arguments>
    </use_mcp_tool>
</execute_mcp>
```
If any tools are connected, they’ll appear below:  
{available_tools}

Focus on tools that offer direct value for the user’s current task.  
Suggest what naturally fits as the next step in their workflow.
"""  # noqa

no_mcp_tool = """
Keep in mind these available MCP tools:
{available_tools}

When relevant to the user's task, suggest appropriate MCP tools with proper parameters.
Tool suggestions should be complete, properly formatted, and ready to execute.
Focus on tools that enhance the user's current workflow and provide immediate utility.
"""  # noqa

mcp_tool_reminder = """
Tool calls should be complete, properly parameterized, and executable.
Format: 
```xml
<use_mcp_tool>
    <server_name>server name here</server_name>
    <tool_name>tool name here</tool_name>
    <arguments>
    {{
      "param1": "value1",
      "param2": "value2"
    }}
    </arguments>
</use_mcp_tool>
```
Available tools: {available_tools}
"""  # noqa
