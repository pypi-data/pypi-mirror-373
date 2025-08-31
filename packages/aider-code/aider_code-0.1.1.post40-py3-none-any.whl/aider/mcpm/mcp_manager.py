import asyncio
import queue
import threading
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml
import json
from mcp import ClientSession, StdioServerParameters, stdio_client

from .mcp_server import McpServer
from .mcp_tool import McpTool
from ..waiting import WaitingSpinner


@dataclass
class CallArguments:
    server_name: str
    function: str
    args: dict


@dataclass
class CallResponse:
    error: str | None
    response: str | None


class McpManager:
    """Manages MCP servers and tools configuration."""

    event_loop = None  # 클래스 변수 (static 역할)

    def __init__(self, i18n=None):
        self.i18n = i18n
        self.servers: Dict[str, McpServer] = {}
        self.enabled: bool = False
        self.message_queue = queue.Queue()
        self.result_queue = queue.Queue()
        # Dictionary to store client sessions for different servers
        self.server_sessions = {}
        self.is_running = False

    def configure_from_args(self, args) -> None:
        """Configure MCP from command-line arguments."""
        self.enabled = args.mcp

        # If MCP is not enabled, don't process further
        if not self.enabled:
            return

        conf_fnames = [
            Path(".aider.mcp.conf.yml"),
            Path(".aider.mcp.conf.yaml"),
            Path(".aider.mcp.conf.json"),
        ]
        default_config_files = []
        try:
            for conf_fname in conf_fnames:
                default_config_files += [conf_fname.resolve()]
        except OSError:
            pass
        for conf_fname in conf_fnames:
            default_config_files.append(
                Path.home() / ".devflux" / ".aider" / conf_fname
            )  # homedir

        default_config_files = list(map(str, default_config_files))
        default_config_files.reverse()

        # 첫 번째로 확인되는 설정 파일 로드
        for config_file in default_config_files:
            if Path(config_file).exists() and Path(config_file).suffix in [".json"]:
                self._load_json_config_file(config_file)
                break

            if Path(config_file).exists() and Path(config_file).suffix in [
                ".yml",
                ".yaml",
            ]:
                self._load_yaml_config_file(config_file)
                break

    def _load_json_config_file(self, config_file: str) -> None:
        """Load server configurations from a JSON config file."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 서버 설정이 리스트 형태로 들어올 경우
            servers = config.get("mcpServers", [])
            if not isinstance(servers, list):
                servers = [servers]

            for server_config in servers:
                server_name = server_config.get("name")
                if not server_name:
                    continue

                server = self.add_server(server_name)
                # 서버 속성 설정
                for key, value in server_config.items():
                    if hasattr(server, key):
                        setattr(server, key, value)

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading JSON config file {config_file}: {e}")

    def _load_yaml_config_file(self, config_file: str) -> None:
        """Load server configurations from a YAML config file."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 서버 설정이 리스트 형태로 들어올 경우
            servers = config.get("mcpServers", [])
            if not isinstance(servers, list):
                servers = [servers]

            for server_config in servers:
                server_name = server_config.get("name")
                if not server_name:
                    continue

                server = self.add_server(server_name)
                # 서버 속성 설정
                for key, value in server_config.items():
                    if hasattr(server, key):
                        setattr(server, key, value)

        except (yaml.YAMLError, IOError) as e:
            print(f"Error loading YAML config file {config_file}: {e}")

    def initialize_servers(self, io) -> None:
        """Initialize and start all enabled MCP servers.

        Args:
            io: InputOutput object for logging messages
            :param io:
        """
        if not self.enabled:
            return

        self.is_running = True
        loop = McpManager._get_event_loop()

        for server in self.get_enabled_servers():
            if server.command:
                t = threading.Thread(target=self._server_loop, args=(loop,))
                t.start()
            else:
                io.tool_warning(f"MCP server '{server.name}' has no command configured")

    def discover_tools(self, io) -> None:
        """Discover tools from all enabled servers.

        Args:
            io: InputOutput object for logging messages
        """
        if not self.enabled:
            return

        for server in self.get_enabled_servers():
            # Check if the server configuration is valid
            if not server.is_valid():
                if io:
                    io.tool_warning(
                        f"Cannot discover tools for server '{server.name}': Invalid configuration (must have a command)"
                    )
                continue

            response = self._call(io, server.name, "list_tools", {})

            # Process the tools
            for tool in response.tools:
                name = tool.name
                description = tool.description
                input_schema = tool.inputSchema

                # Get the permission from the existing tool configuration or default to "manual"
                permission = server.permissions.get(name, "manual")
                title = tool.title if hasattr(tool, "title") else None
                required = tool.required if hasattr(tool, "required") else None
                output_schema = (
                    tool.outputSchema if hasattr(tool, "outputSchema") else None
                )
                annotations = tool.annotations if hasattr(tool, "annotations") else None
                meta = tool.meta if hasattr(tool, "meta") else None

                # Add the tool to the server configuration
                server.add_tool(
                    name,
                    title,
                    description,
                    required,
                    input_schema,
                    output_schema,
                    annotations,
                    meta,
                    permission,
                )

    @staticmethod
    def _get_event_loop() -> asyncio.AbstractEventLoop:
        """Get the current event loop or create a new one if none exists."""
        try:
            if McpManager.event_loop is None:
                loop = asyncio.new_event_loop()
                McpManager.event_loop = loop
            else:
                loop = McpManager.event_loop
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            McpManager.event_loop = loop
            return loop

    def _call(self, io, server_name, function, args: dict = {}):
        """Sync call to the thread with queues.

        Raises:
            KeyboardInterrupt: ctrl+c가 눌렸을 때 발생
        """
        try:
            self.message_queue.put(CallArguments(server_name, function, args))
            with WaitingSpinner(f"Waiting for {server_name}"):
                result = self.result_queue.get()
                self.result_queue.task_done()

            if result.error:
                if io:
                    io.tool_error(result.error)
                return None

            return result.response
        except KeyboardInterrupt:
            if io:
                io.tool_error("\nThe program has been stopped by the user.")
            raise

    def _server_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Wrap the async server loop for a given server."""

        try:
            if not loop.is_running():
                loop.run_until_complete(self._async_server_loop())
        except KeyboardInterrupt:
            raise
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[ERROR] Server loop error : {e}")

    async def _create_server_session(
        self, server: McpServer, exit_stack: AsyncExitStack
    ) -> Optional[ClientSession]:
        """Create a new server session.

        Args:
            server: The server configuration to create a session for
            exit_stack: AsyncExitStack for managing resources

        Returns:
            ClientSession if successful, None otherwise
        """
        if not server or not server.command:
            return None

        if server.name in self.server_sessions:
            return self.server_sessions[server.name]

        try:
            server_params = StdioServerParameters(
                command=server.command,
                args=server.args,
                env=server.env or {} or None,
            )

            stdio_transport = await exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            stdio, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await session.initialize()
            if not session:
                return None

            self.server_sessions[server.name] = session
            return session

        except Exception as e:
            print(f"[ERROR] Failed to create session for {server.name}: {str(e)}")
            return None

    async def _async_server_loop(self) -> None:
        """서버 메시지 라우팅을 담당하는 async 루프 개선 버전."""
        try:
            async with AsyncExitStack() as exit_stack:
                # 서버 세션 초기화
                for server in self.get_enabled_servers():
                    session = await self._create_server_session(server, exit_stack)
                    if not session:
                        continue

                while self.is_running:
                    try:
                        # 메시지 가져오기 (비동기적으로 대기)
                        try:
                            msg = await McpManager.event_loop.run_in_executor(
                                None, self.message_queue.get_nowait
                            )
                            if not msg:
                                continue
                        except queue.Empty:
                            await asyncio.sleep(
                                0.1
                            )  # CPU 사용량을 줄이기 위한 짧은 대기
                            continue

                        # 종료 메시지 처리
                        if msg and msg.function == "exit":
                            self.message_queue.task_done()
                            break

                        target_server = msg.server_name
                        target_session = self.server_sessions.get(target_server)

                        # 세션 없으면 생성
                        if not target_session:
                            target_server_obj = self.servers.get(target_server)
                            if not target_server_obj:
                                self.result_queue.put(
                                    CallResponse(
                                        f"Unknown server: {target_server}", None
                                    )
                                )
                                self.message_queue.task_done()
                                continue

                            target_session = await self._create_server_session(
                                target_server_obj, exit_stack
                            )
                            if not target_session:
                                self.result_queue.put(
                                    CallResponse(
                                        f"Failed to initialize session for {target_server}",
                                        None,
                                    )
                                )
                                self.message_queue.task_done()
                                continue

                            self.server_sessions[target_server] = target_session

                        # 메시지 처리
                        try:
                            if msg.function == "call_tool":
                                response = await target_session.call_tool(**msg.args)
                                self.result_queue.put(CallResponse(None, response))
                            elif msg.function == "list_tools":
                                response = await target_session.list_tools()
                                self.result_queue.put(CallResponse(None, response))
                            else:
                                self.result_queue.put(
                                    CallResponse(
                                        f"Unknown function: {msg.function}", None
                                    )
                                )
                        except Exception as e:
                            print(f"[ERROR] Error processing {msg.function}: {e}")
                            self.result_queue.put(
                                CallResponse(f"Error in {msg.function}: {str(e)}", None)
                            )

                    except (asyncio.CancelledError, KeyboardInterrupt):
                        raise
                    except Exception as e:
                        raise
                    finally:
                        # 메시지 처리 완료 표시 (한 번만 호출)
                        if msg is not None:
                            try:
                                self.message_queue.task_done()
                            except ValueError:
                                # 이미 task_done이 호출된 경우 무시
                                pass

        except (asyncio.CancelledError, KeyboardInterrupt):
            print("[INFO] Server loop interrupted by user")
            raise
        except Exception as e:
            print(f"[CRITICAL] Server loop error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            # 큐 정리 (에러 발생 시에도 실행)
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                    self.message_queue.task_done()
                except (queue.Empty, ValueError):
                    break

    def add_server(self, server_name: str) -> McpServer:
        """Add a new server if it doesn't exist, or return the existing one."""
        if server_name not in self.servers:
            self.servers[server_name] = McpServer(server_name)
        return self.servers[server_name]

    def get_server(self, server_name: str) -> Optional[McpServer]:
        """Get a server by name, or None if it doesn't exist."""
        return self.servers.get(server_name)

    def get_enabled_servers(self) -> List[McpServer]:
        """Get a list of all enabled servers."""
        return [server for server in self.servers.values() if server.enabled]

    def list_servers(self) -> List[McpServer]:
        """Get a list of all servers."""
        return list(self.servers.values())

    def list_tools(self) -> Dict[str, List[McpTool]]:
        """Get a dictionary of server names to lists of tools."""
        result = {}
        for server_name, server in self.servers.items():
            if server.tools:
                result[server_name] = list(server.tools.values())
        return result

    def execute_tool(
        self, server_name: str, tool_name: str, arguments: dict, io
    ) -> str:
        """Execute an MCP tool with the given arguments.

        Args:
            server_name: The name of the server providing the tool
            tool_name: The name of the tool to execute
            arguments: A dictionary of arguments to pass to the tool
            io: InputOutput object for logging messages

        Returns:
            The result of the tool execution as a string
        """
        if not self.enabled:
            io.tool_error("MCP is not enabled")
            return "MCP is not enabled"

        server = self.get_server(server_name)
        if not server:
            io.tool_error(f"MCP server '{server_name}' not found")
            return f"MCP server '{server_name}' not found"

        if not server.enabled:
            io.tool_error(f"MCP server '{server_name}' is not enabled")
            return f"MCP server '{server_name}' is not enabled"

        if tool_name not in server.tools:
            io.tool_error(f"Tool '{tool_name}' not found in server '{server_name}'")
            return f"Tool '{tool_name}' not found in server '{server_name}'"

        # Get the tool permission
        tool = server.tools[tool_name]
        permission = tool.permission

        # Check if the tool requires manual approval
        if permission == "manual":
            if not io.confirm_ask(
                self.i18n.t("ask.014", tool_name=tool_name, server_name=server_name)
            ):
                return self.i18n.t("ask.015")

        # Execute the tool
        try:
            response = self._call(
                io,
                server_name,
                "call_tool",
                {"name": tool_name, "arguments": arguments},
            )

            # Process the response
            result = ""
            for content_item in response.content:
                if content_item.type == "text":
                    result += content_item.text

            io.tool_output(f"Tool '{tool_name}' executed successfully")

            return result
        except KeyboardInterrupt:
            io.tool_error("\nThe program has been stopped by the user.")
            raise
        except asyncio.CancelledError:
            io.tool_error("\nThe program has been stopped by the user.")
            raise
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            io.tool_error(error_msg)
            return error_msg

    def stop_servers(self) -> None:
        """Stop all running MCP servers."""
        self.message_queue.put(CallArguments("", "exit", {}))
        self.is_running = False
