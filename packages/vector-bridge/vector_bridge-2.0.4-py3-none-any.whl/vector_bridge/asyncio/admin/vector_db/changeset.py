from typing import Any, Dict, List, Optional, Union

from weaviate.classes.config import Tokenization

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.vectordb_state_changeset import \
    raise_for_vectordb_state_changeset_detail
from vector_bridge.schema.helpers.enums import (DataTypeInput, FilterKey,
                                                FilterOperator, PropertyKey)
from vector_bridge.schema.weaviate_schema import StateFullSchema


class AsyncVectorDBChangesetAdmin:
    """Async admin client for vector database changeset management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def get_changeset_diff(self, integration_name: Optional[str] = None) -> List[StateFullSchema]:
        """
        Get the changeset diff.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/diff"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def add_schema(
        self,
        schema_name: str,
        schema_description: str,
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Add creation of the new Schema to the changeset.

        Args:
            schema_name: The name of the Schema
            schema_description: The description of the Schema
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/schema/add"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        payload = {"schema_name": schema_name, "schema_description": schema_description}

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=payload) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def delete_schema(self, schema_name: str, integration_name: Optional[str] = None) -> List[StateFullSchema]:
        """
        Add deletion of existing Schema to the changeset.

        Args:
            schema_name: The name of the Schema
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/schema/delete"
        params = {"schema_name": schema_name}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def add_property(
        self,
        schema_name: str,
        property_name: str,
        property_description: str,
        data_type: DataTypeInput,
        sorting_supported: bool,
        returned: bool,
        integration_name: Optional[str] = None,
        tokenization: Tokenization = Tokenization.WORD,
    ) -> List[StateFullSchema]:
        """
        Add creation of the property to the changeset schema.

        Args:
            schema_name: The name of the Schema
            property_name: The property name
            property_description: The property description
            data_type: The property data type
            sorting_supported: If sorting supported
            returned: If property should be returned
            integration_name: Specifies the name of the integration module being queried
            tokenization: The tokenization of the text field

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/property/add"
        params = {"data_type": data_type, "tokenization": tokenization}
        if integration_name:
            params["integration_name"] = integration_name

        payload = {
            "schema_name": schema_name,
            "property_name": property_name,
            "property_description": property_description,
            "sorting_supported": sorting_supported,
            "returned": returned,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=payload) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def edit_property(
        self,
        schema_name: str,
        property_name: str,
        key: PropertyKey,
        value: Union[str, bool],
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Update Property.

        Args:
            schema_name: The name of the Schema
            property_name: The property name
            key: The property key
            value: The property value
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/property/edit"
        params = {
            "schema_name": schema_name,
            "property_name": property_name,
            "key": key,
            "value": value,
        }
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def delete_property(
        self,
        schema_name: str,
        property_name: str,
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Add deletion of the property to the changeset.

        Args:
            schema_name: The name of the Schema
            property_name: The property name
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/property/delete"
        params = {"schema_name": schema_name, "property_name": property_name}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def add_filter(
        self,
        schema_name: str,
        property_name: str,
        filter_name: str,
        filter_description: str,
        operator: FilterOperator,
        filtering_supported: bool,
        operator_settings: Dict[str, Any],
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Add creation of the filter to the changeset schema.

        Args:
            schema_name: The name of the Schema
            property_name: The property name
            filter_name: The filter name
            filter_description: The filter description
            operator: The filter operator
            filtering_supported: If filtering supported
            operator_settings: The advanced operator settings
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/filter/add"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        payload = {
            "schema_name": schema_name,
            "property_name": property_name,
            "filter_name": filter_name,
            "filter_description": filter_description,
            "operator": operator,
            "filtering_supported": filtering_supported,
            "operator_settings": operator_settings,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=payload) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def edit_filter(
        self,
        schema_name: str,
        property_name: str,
        filter_name: str,
        key: FilterKey,
        value: Union[str, bool],
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Update Filter.

        Args:
            schema_name: The name of the Schema
            property_name: The property name
            filter_name: The filter name
            key: The filter key
            value: The filter value
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/filter/edit"
        params = {
            "schema_name": schema_name,
            "property_name": property_name,
            "filter_name": filter_name,
            "key": key,
            "value": value,
        }
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]

    async def delete_filter(
        self,
        schema_name: str,
        property_name: str,
        filter_name: str,
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Add deletion of the existing filter to the changeset.

        Args:
            schema_name: The name of the Schema
            property_name: The property name
            filter_name: The filter name
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schema changes in the current changeset
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-db/changeset/filter/delete"
        params = {
            "schema_name": schema_name,
            "property_name": property_name,
            "filter_name": filter_name,
        }
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response,
                error_callable=raise_for_vectordb_state_changeset_detail,
            )
            return [StateFullSchema.model_validate(result) for result in results]
