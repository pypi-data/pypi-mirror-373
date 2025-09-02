from enum import Enum
from typing import Any, Callable, Dict, TypeVar, Union
from urllib.parse import urlparse

import aiohttp
import requests
from pydantic import BaseModel

from vector_bridge.schema.error import HTTPException
from vector_bridge.schema.errors.base import raise_for_base_error_detail

# Type definitions from OpenAPI spec
T = TypeVar("T")


# Models based on OpenAPI schema
class Token(BaseModel):
    access_token: str
    token_type: str


class BaseVectorBridgeClient:
    """Base class for VectorBridge clients with common functionality."""

    def __init__(
        self,
        base_url: str = "http://vector_bridge:8000/",
        api_key: str = None,
        integration_name: str = "default",
    ):
        self.base_url = base_url.rstrip("/")
        self.access_token = None
        self.api_key = api_key
        self.integration_name = integration_name

        self._parsed_url = urlparse(self.base_url)

    @property
    def host(self) -> str:
        return self._parsed_url.hostname or "localhost"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.host}:6379"

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with API key authentication and bearer token authentication."""
        api_key_headers = {}
        if self.api_key:
            api_key_headers["Api-Key"] = self.api_key
        if self.access_token:
            api_key_headers["Authorization"] = f"Bearer {self.access_token}"

        if not api_key_headers:
            raise ValueError("Authentication or API key required. Call login() first or provide api_key.")
        return api_key_headers

    def _create_http_exception(self, status_code: int, error_data: Any, error_callable: Callable) -> Exception:
        """Create HTTPException from error response."""
        if isinstance(error_data, dict):
            detail = error_data.get("detail")
        else:
            detail = str(error_data)

        return error_callable(detail)

    def _print_welcome_message(self, username: str):
        """Print welcome message after login."""
        print(f"Hey, {username}! You have been logged in...")
        print(
            """

██╗   ██╗███████╗ ██████╗████████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗██████╗  ██████╗ ███████╗    █████╗ ██╗
██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝   ██╔══██╗██║
██║   ██║█████╗  ██║        ██║   ██║   ██║██████╔╝██████╔╝██████╔╝██║██║  ██║██║  ███╗█████╗     ███████║██║
╚██╗ ██╔╝██╔══╝  ██║        ██║   ██║   ██║██╔══██╗██╔══██╗██╔══██╗██║██║  ██║██║   ██║██╔══╝     ██╔══██║██║
 ╚████╔╝ ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║██████╔╝██║  ██║██║██████╔╝╚██████╔╝███████╗██╗██║  ██║██║
  ╚═══╝  ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═╝╚═╝
DOCS: https://docs.vectorbridge.ai/                                                           version: 2.0.4

                """
        )


class VectorBridgeClient(BaseVectorBridgeClient):
    """
    Synchronous Python client for the VectorBridge.ai API.

    Provides access to all functionality of the VectorBridge platform including
    authentication, user management, AI processing, vector operations, and more.
    """

    def __init__(
        self,
        base_url: str = "http://vector_bridge:8000/",
        api_key: str = None,
        integration_name: str = "default",
    ):
        """
        Initialize the VectorBridge client.

        Args:
            base_url: The base URL of the VectorBridge API.
            api_key: API key for authentication.
            integration_name: Name of the integration.
        """
        super().__init__(base_url, api_key, integration_name)

        from vector_bridge.sync.admin import AdminClient
        from vector_bridge.sync.client.ai import AIClient
        from vector_bridge.sync.client.ai_message import AIMessageClient
        from vector_bridge.sync.client.function import FunctionClient
        from vector_bridge.sync.client.query import QueryClient
        from vector_bridge.sync.client.workflows import WorkflowClient

        self.session = requests.Session()

        # Initialize client modules
        self.admin = AdminClient(self)
        self.ai = AIClient(self)
        self.ai_message = AIMessageClient(self)
        self.functions = FunctionClient(self)
        self.workflows = WorkflowClient(self)
        self.queries = QueryClient(self)

    def login(self, username: str, password: str) -> Token:
        """
        Log in to obtain an access token.

        Args:
            username: User's email
            password: User's password

        Returns:
            Token object containing access_token and token_type
        """
        url = f"{self.base_url}/token"
        data = {
            "username": username,
            "password": password,
        }
        response = self.session.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        result = self._handle_response(response=response, error_callable=raise_for_base_error_detail)
        self.access_token = result["access_token"]

        self._print_welcome_message(username)

        return Token(**result)

    def _handle_response(self, response: requests.Response, error_callable: Callable) -> Any:
        """Handle API response and errors."""
        if 200 <= response.status_code < 300:
            if response.status_code == 204:
                return None
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text

            exc = self._create_http_exception(response.status_code, error_data, error_callable)
            raise exc

    def ping(self) -> str:
        """
        Ping the API to check if it's available.

        Returns:
            Response string
        """
        url = f"{self.base_url}/v1/ping"
        response = self.session.get(url)
        return self._handle_response(response=response, error_callable=raise_for_base_error_detail)

    def generate_crypto_key(self) -> str:
        """
        Generate a crypto key.

        Returns:
            Generated crypto key
        """
        url = f"{self.base_url}/v1/secrets/generate-crypto-key"
        response = self.session.get(url)
        return self._handle_response(response=response, error_callable=raise_for_base_error_detail)

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncVectorBridgeClient(BaseVectorBridgeClient):
    """
    Asynchronous Python client for the VectorBridge.ai API.

    Provides async access to all functionality of the VectorBridge platform including
    authentication, user management, AI processing, vector operations, and more.
    """

    def __init__(
        self,
        base_url: str = "http://vector_bridge:8000/",
        api_key: str = None,
        integration_name: str = "default",
        connector: aiohttp.BaseConnector = None,
        timeout: aiohttp.ClientTimeout = None,
    ):
        """
        Initialize the async VectorBridge client.

        Args:
            base_url: The base URL of the VectorBridge API.
            api_key: API key for authentication.
            integration_name: Name of the integration.
            connector: aiohttp connector for custom connection handling.
            timeout: Timeout configuration for requests.
        """
        super().__init__(base_url, api_key, integration_name)

        from vector_bridge.asyncio.admin import AsyncAdminClient
        from vector_bridge.asyncio.client.ai import AsyncAIClient
        from vector_bridge.asyncio.client.ai_message import \
            AsyncAIMessageClient
        from vector_bridge.asyncio.client.function import AsyncFunctionClient
        from vector_bridge.asyncio.client.query import AsyncQueryClient
        from vector_bridge.asyncio.client.workflows import AsyncWorkflowClient

        self.session = None
        self._connector = connector
        self._timeout = timeout or aiohttp.ClientTimeout(total=30)

        # Initialize async client modules
        if AsyncAdminClient:
            self.admin = AsyncAdminClient(self)
            self.ai = AsyncAIClient(self)
            self.ai_message = AsyncAIMessageClient(self)
            self.functions = AsyncFunctionClient(self)
            self.workflows = AsyncWorkflowClient(self)
            self.queries = AsyncQueryClient(self)

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self.session is None:
            self.session = aiohttp.ClientSession(connector=self._connector, timeout=self._timeout)

    async def login(self, username: str, password: str) -> Token:
        """
        Log in to obtain an access token.

        Args:
            username: User's email
            password: User's password

        Returns:
            Token object containing access_token and token_type
        """
        await self._ensure_session()

        url = f"{self.base_url}/token"
        data = aiohttp.FormData()
        data.add_field("username", username)
        data.add_field("password", password)

        async with self.session.post(url, data=data) as response:
            result = await self._handle_response(response=response, error_callable=raise_for_base_error_detail)
            self.access_token = result["access_token"]

            # Print welcome message in sync context (or make it optional)
            self._print_welcome_message(username)

            return Token(**result)

    async def _handle_response(self, response: aiohttp.ClientResponse, error_callable: Callable) -> Any:
        """Handle async API response and errors."""
        if 200 <= response.status < 300:
            if response.status == 204:
                return None
            try:
                return await response.json()
            except (ValueError, aiohttp.ContentTypeError):
                return await response.text()
        else:
            try:
                error_data = await response.json()
            except (ValueError, aiohttp.ContentTypeError):
                error_data = await response.text()

            exc = self._create_http_exception(response.status, error_data, error_callable)
            raise exc

    async def ping(self) -> str:
        """
        Ping the API to check if it's available.

        Returns:
            Response string
        """
        await self._ensure_session()

        url = f"{self.base_url}/v1/ping"
        async with self.session.get(url) as response:
            return await self._handle_response(response=response, error_callable=raise_for_base_error_detail)

    async def generate_crypto_key(self) -> str:
        """
        Generate a crypto key.

        Returns:
            Generated crypto key
        """
        await self._ensure_session()

        url = f"{self.base_url}/v1/secrets/generate-crypto-key"
        async with self.session.get(url) as response:
            return await self._handle_response(response=response, error_callable=raise_for_base_error_detail)

    async def close(self):
        """Close the async session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None


# Factory function for easier client creation
def create_client(
    base_url: str = "http://vector_bridge:8000/",
    api_key: str = None,  # TODO: Add ADMIN API KEY support (That's basically an admin's ACCESS TOKEN)
    integration_name: str = "default",
    async_client: bool = False,
    **kwargs,
) -> Union[VectorBridgeClient, AsyncVectorBridgeClient]:
    """
    Factory function to create either sync or async VectorBridge client.

    Args:
        base_url: The base URL of the VectorBridge API.
        api_key: API key for authentication.
        integration_name: Name of the integration.
        async_client: If True, returns AsyncVectorBridgeClient, otherwise VectorBridgeClient.
        **kwargs: Additional arguments passed to the client constructor.

    Returns:
        VectorBridgeClient or AsyncVectorBridgeClient instance.
    """
    if async_client:
        return AsyncVectorBridgeClient(
            base_url=base_url,
            api_key=api_key,
            integration_name=integration_name,
            **kwargs,
        )
    else:
        return VectorBridgeClient(
            base_url=base_url,
            api_key=api_key,
            integration_name=integration_name,
        )
