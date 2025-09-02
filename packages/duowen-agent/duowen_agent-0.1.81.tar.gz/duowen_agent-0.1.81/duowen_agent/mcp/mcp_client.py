import logging
from collections.abc import Callable
from contextlib import AbstractContextManager, ExitStack
from types import TracebackType
from typing import Any, Optional, cast
from urllib.parse import urlparse

from duowen_agent.mcp.client.sse_client import sse_client
from duowen_agent.mcp.client.streamable_client import streamablehttp_client
from duowen_agent.mcp.error import MCPAuthError, MCPConnectionError
from duowen_agent.mcp.session.client_session import ClientSession
from duowen_agent.mcp.types import Tool, OAuthTokens

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(
        self,
        server_url: str,
        authed: bool = True,
        token: Optional[OAuthTokens] = None,
        authorization_code: Optional[str] = None,
    ):
        # Initialize info
        self.client_type = "streamable"
        self.server_url = server_url

        # Authentication info
        self.authed = authed
        self.authorization_code = authorization_code
        if authed:
            self.token = token

        # Initialize session and client objects
        self._session: Optional[ClientSession] = None
        self._streams_context: Optional[AbstractContextManager[Any]] = None
        self._session_context: Optional[ClientSession] = None
        self.exit_stack = ExitStack()

        # Whether the client has been initialized
        self._initialized = False

    def __enter__(self):
        self._initialize()
        self._initialized = True
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ):
        self.cleanup()

    def _initialize(
        self,
    ):
        """Initialize the client with fallback to SSE if streamable connection fails"""
        connection_methods: dict[str, Callable[..., AbstractContextManager[Any]]] = {
            "mcp": streamablehttp_client,
            "sse": sse_client,
        }

        parsed_url = urlparse(self.server_url)
        path = parsed_url.path or ""
        method_name = path.rstrip("/").split("/")[-1] if path else ""
        if method_name in connection_methods:
            client_factory = connection_methods[method_name]
            self.connect_server(client_factory, method_name)
        else:
            try:
                logger.debug(
                    "Not supported method %s found in URL path, trying default 'mcp' method.",
                    method_name,
                )
                self.connect_server(sse_client, "sse")
            except MCPConnectionError:
                logger.debug(
                    "MCP connection failed with 'sse', falling back to 'mcp' method."
                )
                self.connect_server(streamablehttp_client, "mcp")

    def connect_server(
        self,
        client_factory: Callable[..., AbstractContextManager[Any]],
        method_name: str,
        first_try: bool = True,
    ):

        try:
            headers = (
                {
                    "Authorization": f"{self.token.token_type.capitalize()} {self.token.access_token}"
                }
                if self.authed and self.token
                else {}
            )
            self._streams_context = client_factory(url=self.server_url, headers=headers)
            if not self._streams_context:
                raise MCPConnectionError("Failed to create connection context")

            # Use exit_stack to manage context managers properly
            if method_name == "mcp":
                read_stream, write_stream, _ = self.exit_stack.enter_context(
                    self._streams_context
                )
                streams = (read_stream, write_stream)
            else:  # sse_client
                streams = self.exit_stack.enter_context(self._streams_context)

            self._session_context = ClientSession(*streams)
            self._session = self.exit_stack.enter_context(self._session_context)
            session = cast(ClientSession, self._session)
            session.initialize()
            return

        except MCPAuthError:
            if not self.authed:
                raise

            if first_try:
                return self.connect_server(client_factory, method_name, first_try=False)

        except MCPConnectionError:
            raise

    def list_tools(self) -> list[Tool]:
        """Connect to an MCP server running with SSE transport"""
        # List available tools to verify connection
        if not self._initialized or not self._session:
            raise ValueError("Session not initialized.")
        response = self._session.list_tools()
        tools = response.tools
        return tools

    def invoke_tool(self, tool_name: str, tool_args: dict):
        """Call a tool"""
        if not self._initialized or not self._session:
            raise ValueError("Session not initialized.")
        return self._session.call_tool(tool_name, tool_args)

    def cleanup(self):
        """Clean up resources"""
        try:
            # ExitStack will handle proper cleanup of all managed context managers
            self.exit_stack.close()
        except Exception as e:
            logging.exception("Error during cleanup")
            raise ValueError(f"Error during cleanup: {e}")
        finally:
            self._session = None
            self._session_context = None
            self._streams_context = None
            self._initialized = False
