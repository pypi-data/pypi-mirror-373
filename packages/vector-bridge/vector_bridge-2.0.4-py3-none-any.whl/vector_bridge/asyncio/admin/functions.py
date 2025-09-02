import json
from typing import Any, Callable, Dict, Optional, Union

from pydantic import BaseModel

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.functions import raise_for_function_detail
from vector_bridge.schema.functions import (CodeExecuteFunctionCreate,
                                            CodeExecuteFunctionUpdate,
                                            Function, FunctionExtractor,
                                            JsonFunctionCreate,
                                            JsonFunctionUpdate,
                                            PaginatedFunctions,
                                            SemanticSearchFunctionCreate,
                                            SemanticSearchFunctionUpdate,
                                            SimilarSearchFunctionCreate,
                                            SimilarSearchFunctionUpdate,
                                            SummaryFunctionCreate,
                                            SummaryFunctionUpdate)


class AsyncFunctionsAdmin:
    """Async admin client for functions management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def add_function(
        self,
        function_data: Union[
            SemanticSearchFunctionCreate,
            SimilarSearchFunctionCreate,
            SummaryFunctionCreate,
            JsonFunctionCreate,
            CodeExecuteFunctionCreate,
        ],
        integration_name: str = None,
    ) -> Function:
        """
        Add new Function to the integration.

        Args:
            function_data: Function details
            integration_name: The name of the Integration

        Returns:
            Created function object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.post(
            url, headers=headers, params=params, json=function_data.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_function_detail)
            return Function.to_valid_subclass(result)

    async def add_python_function(
        self,
        function: Callable,
        integration_name: str = None,
    ) -> Function:
        """
        Add a Python function directly.

        This automatically extracts the function's code, signature, and documentation
        to create a CODE_EXEC function that can be called remotely.

        Args:
            function: The Python function to add (must have type annotations and docstrings)
            integration_name: The name of the Integration

        Returns:
            Created function object
        """
        # Extract function metadata and code
        extractor = FunctionExtractor(function)
        function_data = extractor.get_function_metadata()

        # Create the CodeExecuteFunctionCreate model
        function_model = CodeExecuteFunctionCreate.model_validate(function_data)

        # Call the existing add_function method
        return await self.add_function(function_model, integration_name)

    async def get_function_by_name(self, function_name: str, integration_name: str = None) -> Optional[Function]:
        """
        Get the Function by name.

        Args:
            function_name: The name of the Function
            integration_name: The name of the Integration

        Returns:
            Function object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function"
        params = {"integration_name": integration_name, "function_name": function_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            if response.status == 404:
                return None

            result = await self.client._handle_response(response=response, error_callable=raise_for_function_detail)
            return Function.to_valid_subclass(result)

    async def get_function_by_id(self, function_id: str, integration_name: str = None) -> Optional[Function]:
        """
        Get the Function by ID.

        Args:
            function_id: The ID of the Function
            integration_name: The name of the Integration

        Returns:
            Function object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function/{function_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            if response.status == 404:
                return None

            result = await self.client._handle_response(response=response, error_callable=raise_for_function_detail)
            return Function.to_valid_subclass(result)

    async def update_function(
        self,
        function_id: str,
        function_data: Union[
            SemanticSearchFunctionUpdate,
            SimilarSearchFunctionUpdate,
            SummaryFunctionUpdate,
            JsonFunctionUpdate,
            CodeExecuteFunctionUpdate,
        ],
        integration_name: str = None,
    ) -> Function:
        """
        Update an existing Function.

        Args:
            function_id: The ID of the Function to update
            function_data: Updated function details
            integration_name: The name of the Integration

        Returns:
            Updated function object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function/{function_id}/update"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.put(
            url, headers=headers, params=params, json=function_data.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_function_detail)
            return Function.to_valid_subclass(result)

    async def list_functions(
        self,
        integration_name: str = None,
        limit: int = 10,
        last_evaluated_key: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> PaginatedFunctions:
        """
        List Functions for an Integration.

        Args:
            integration_name: The name of the Integration
            limit: Number of functions to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: Field to sort by (created_at or updated_at)

        Returns:
            Dict with functions and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/functions/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "sort_by": sort_by,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_function_detail)
            return PaginatedFunctions.resolve_functions(result)

    async def list_default_functions(
        self,
    ) -> PaginatedFunctions:
        """
        List Functions for an Integration.

        Args:
            integration_name: The name of the Integration
            limit: Number of functions to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: Field to sort by (created_at or updated_at)

        Returns:
            Dict with functions and pagination info
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/functions/list-default"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_function_detail)
            return PaginatedFunctions.resolve_functions(result)

    async def delete_function(self, function_id: str, integration_name: str = None) -> None:
        """
        Delete a function.

        Args:
            function_id: The ID of the function to delete
            integration_name: The name of the Integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function/{function_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_function_detail)
