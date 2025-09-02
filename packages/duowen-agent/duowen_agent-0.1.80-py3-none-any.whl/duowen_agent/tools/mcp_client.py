import asyncio
import json
import os
import threading
from contextlib import AsyncExitStack
from typing import Dict, Any, List

import pydantic
from duowen_agent.error import ToolError
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import (
    ListToolsResult,
    ListResourcesResult,
    ListPromptsResult,
)
from mcp.types import TextContent


class McpClient:
    def __init__(
        self, mcp_config_json: Dict[str, Any], filter_function_list: List[str] = None
    ):
        self.exit_stack = AsyncExitStack()
        self.mcp_sessions: dict[str, ClientSession] = {}
        self.filter_function_list = filter_function_list

        # added shared "event loop" and user counter as class variables
        self._shared_loop = None
        self._loop_users = 0
        self._loop_lock = threading.Lock()  # lock for thread safety
        self.tools = {}
        self.mcp_config_json = mcp_config_json
        self._init_tools(mcp_config_json)

    @property
    def tool_classifiers(self) -> dict[str, str]:
        _classifiers = {}
        if self.filter_function_list:
            for tool_name, tool_params in self.tools.items():
                if tool_name in self.filter_function_list:
                    _classifiers[tool_name] = tool_params["description"]
        else:
            for tool_name, tool_params in self.tools.items():
                _classifiers[tool_name] = tool_params["description"]
        return _classifiers

    @property
    def tool_descriptions(self) -> str:
        tool_descriptions = ""
        if self.filter_function_list:
            for tool_name, tool_params in self.tools.items():
                if tool_name in self.filter_function_list:
                    tool_descriptions += (
                        json.dumps(
                            {
                                "name": tool_name,
                                "description": tool_params["description"],
                                "parameters": tool_params["inputSchema"],
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        else:
            for tool_name, tool_params in self.tools.items():
                tool_descriptions += (
                    json.dumps(
                        {
                            "name": tool_name,
                            "description": tool_params["description"],
                            "parameters": tool_params.get("inputSchema", {}),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return tool_descriptions

    def get_tool_info(self, tool_name: str):
        return self.tools.get(tool_name, None)

    async def _setup_stdio_mcp(
        self, config_json: dict
    ) -> tuple[ListToolsResult, ListResourcesResult, ListPromptsResult, ClientSession]:
        """Establish stdio MCP client connection (called in _invoke)"""
        server_params = self._get_mcp_server_params_from_config(config_json)
        try:
            transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = transport
            mcp_session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await mcp_session.initialize()
            tool_list, resource_list, prompt_list = await self._get_mcp_action_list(
                mcp_session
            )

            return tool_list, resource_list, prompt_list, mcp_session

        except Exception as e:
            await self._cleanup_mcp()
            raise ToolError(f"Failed to connect to MCP server with stdio: {e}")

    async def _setup_sse_mcp(
        self, config_json: dict
    ) -> tuple[ListToolsResult, ListResourcesResult, ListPromptsResult, ClientSession]:
        """Connect to an MCP server running with SSE transport"""
        mcp_server_url = self._get_mcp_server_url_from_config(config_json)
        try:
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(url=mcp_server_url)
            )
            read, write = sse_transport
            mcp_session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await mcp_session.initialize()
            tool_list, resource_list, prompt_list = await self._get_mcp_action_list(
                mcp_session
            )

            return tool_list, resource_list, prompt_list, mcp_session

        except Exception as e:
            await self._cleanup_mcp()
            raise ToolError(f"Failed to connect to MCP server with SSE: {e}")

    async def _get_mcp_action_list(
        self, mcp_session: ClientSession
    ) -> tuple[ListToolsResult, ListResourcesResult, ListPromptsResult]:
        try:
            # call only the methods that the server has safely
            try:
                tool_list = await mcp_session.list_tools()
            except Exception:
                tool_list = []  # use an empty list if not supported

            try:
                resource_list = await mcp_session.list_resources()
            except Exception:
                resource_list = []

            try:
                prompt_list = await mcp_session.list_prompts()
            except Exception:
                prompt_list = []

            return tool_list, resource_list, prompt_list

        except Exception as e:
            await self._cleanup_mcp()
            raise ToolError(f"Failed to get MCP <tool, resource, prompt> list: {e}")

    def _get_mcp_server_params_from_config(
        self, config_json: dict
    ) -> StdioServerParameters:
        # exsample structure of config

        # "filesystem": {
        #   "command": "npx",
        #   "args": [
        #     "-y",
        #     "@modelcontextprotocol/server-filesystem",
        #     "C:\\Users\\username\\Desktop",
        #     "C:\\Users\\username\\Downloads"
        #   ]
        # }
        command = config_json["command"]
        if command is None:
            raise ToolError("The command must be a valid string and cannot be None.")

        server_params = StdioServerParameters(
            command=command,
            args=config_json["args"],
            env=(
                {**os.environ, **config_json["env"]} if config_json.get("env") else None
            ),
        )

        return server_params

    def _get_mcp_server_url_from_config(self, config_json: dict) -> str:
        """
        "env" is not supported.
        when awaking SSE MCP server.
        """

        # "sse_server_name": {
        #   "url": "http://localhost:3000/sse",
        # }
        url = config_json["url"]
        if url is None:
            raise ToolError("The URL must be a valid string and cannot be None.")

        return url

    async def _cleanup_mcp(self):
        """Clean up MCP Client session."""
        if hasattr(self, "exit_stack") and self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                if "Event loop is closed" not in str(e):
                    print(f"Resource release error: {e}")
            finally:
                self.exit_stack = None
                self.mcp_sessions = None

    def run_tool(self, tool_full_name: str, tool_args: Dict[str, Any]) -> str:
        """
        根据 "serverName_toolName" 格式调用相应 MCP 工具
        """
        if tool_full_name not in self.tools:
            return f"无效的工具名称: {tool_full_name}"

        server_name = self.tools[tool_full_name]["mcp_server_name"]
        name = self.tools[tool_full_name]["name"]
        resp = self._run_async(self._mcp_run_tool(server_name, name, tool_args))

        if isinstance(resp, str):
            return resp
        elif isinstance(resp, TextContent):
            return resp.text
        elif isinstance(resp, list) and all(isinstance(i, TextContent) for i in resp):
            return "\n".join([i.text for i in resp])
        elif isinstance(resp, pydantic.BaseModel):
            return json.dumps(resp.model_dump(), ensure_ascii=False, indent=2)
        else:
            return str(resp)

    async def _mcp_run_tool(
        self, server_name: str, tool_name: str, tool_args: Dict[str, Any]
    ) -> str:
        resp = await self.mcp_sessions[server_name].call_tool(
            name=tool_name, arguments=tool_args
        )
        return resp.content if resp.content else "工具执行无输出"

    def _init_tools(self, mcp_config_json: dict):
        """
        {
            "mcpservers": {
                {
                    "name_of_mcpserver1": {
                        "command": "npx",
                        "args": ["arg1", "arg2"],
                        "env": {"API_KEY": "value"}
                    },
                    "name_of_mcpserver2": {
                        "url": "http://localhost:3000/sse",
                    }
                }
            }
        }
        """
        for mcp_server_name, mcp_server_cmd_or_url in mcp_config_json[
            "mcpServers"
        ].items():

            if mcp_server_cmd_or_url.get("command"):  # stdio (standard I/O)
                # connect to MCP server
                (
                    mcp_tool_list,
                    mcp_resource_list,
                    mcp_prompt_list,
                    self.mcp_sessions[mcp_server_name],
                ) = self._run_async(self._setup_stdio_mcp(mcp_server_cmd_or_url))

            elif mcp_server_cmd_or_url.get("url"):  # SSE
                (
                    mcp_tool_list,
                    mcp_resource_list,
                    mcp_prompt_list,
                    self.mcp_sessions[mcp_server_name],
                ) = self._run_async(self._setup_sse_mcp(mcp_server_cmd_or_url))

            else:
                mcp_tool_list = ListToolsResult(tools=[])

            for tool in mcp_tool_list.tools:
                function_name = f"{mcp_server_name}_{tool.name}"
                self.tools[function_name] = {
                    "mcp_server_name": mcp_server_name,
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }

    def _run_async(self, coroutine):
        """Helper function to run async coroutine synchronously (semaphore method)"""
        try:
            # check if there is a running event loop
            try:
                loop = asyncio.get_running_loop()
                # run on existing event loop
                future = asyncio.run_coroutine_threadsafe(coroutine, loop)
                return future.result(timeout=300)  # 300 seconds is operation timeout
            except RuntimeError:
                # create a new event loop if there is no running loop
                with self._loop_lock:  # lock thread safely
                    # create a shared loop if it does not exist yet
                    if self._shared_loop is None:
                        self._shared_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(self._shared_loop)
                    # increase user count
                    self._loop_users += 1

                loop = self._shared_loop
                try:
                    # run coroutine on shared event loop
                    return loop.run_until_complete(coroutine)

                finally:
                    with self._loop_lock:  # lock thread safely
                        # decrease user count
                        self._loop_users -= 1

        except Exception as e:
            return f"error in async execution: {str(e)}"
