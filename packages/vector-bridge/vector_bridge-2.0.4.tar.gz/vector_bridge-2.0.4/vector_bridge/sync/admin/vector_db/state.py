from typing import List, Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.vectordb_state_changeset import \
    raise_for_vectordb_state_changeset_detail
from vector_bridge.schema.weaviate_schema import StateFullSchema


class VectorDBStateAdmin:
    """Admin client for vector database schema management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def apply_schemas_changes(self, integration_name: Optional[str] = None) -> List[StateFullSchema]:
        """
        Apply VectorDB schemas changes.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schemas with their state information
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/schemas/apply-changes"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        results = self.client._handle_response(
            response=response, error_callable=raise_for_vectordb_state_changeset_detail
        )
        return [StateFullSchema.model_validate(result) for result in results]

    def discard_schemas_changes(self, integration_name: Optional[str] = None) -> List[StateFullSchema]:
        """
        Discard VectorDB schemas changes.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schemas with their state information
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/schemas/discard-changes"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        results = self.client._handle_response(
            response=response, error_callable=raise_for_vectordb_state_changeset_detail
        )
        return [StateFullSchema.model_validate(result) for result in results]

    def discard_schema_changes(self, schema_name: str, integration_name: Optional[str] = None) -> List[StateFullSchema]:
        """
        Discard changes for a specific VectorDB schema.

        Args:
            schema_name: The name of the schema
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schemas with their state information
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/schema/discard-changes"
        params = {"schema_name": schema_name}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        results = self.client._handle_response(
            response=response, error_callable=raise_for_vectordb_state_changeset_detail
        )
        return [StateFullSchema.model_validate(result) for result in results]

    def discard_property_changes(
        self,
        schema_name: str,
        property_name: str,
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Discard changes for a specific property in a VectorDB schema.

        Args:
            schema_name: The name of the schema
            property_name: The name of the property
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schemas with their state information
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/property/discard-changes"
        params = {"schema_name": schema_name, "property_name": property_name}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        results = self.client._handle_response(
            response=response, error_callable=raise_for_vectordb_state_changeset_detail
        )
        return [StateFullSchema.model_validate(result) for result in results]

    def discard_filter_changes(
        self,
        schema_name: str,
        property_name: str,
        filter_name: str,
        integration_name: Optional[str] = None,
    ) -> List[StateFullSchema]:
        """
        Discard changes for a specific filter in a VectorDB schema property.

        Args:
            schema_name: The name of the schema
            property_name: The name of the property
            filter_name: The name of the filter
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of schemas with their state information
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/filters/discard-changes"
        params = {
            "schema_name": schema_name,
            "property_name": property_name,
            "filter_name": filter_name,
        }
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        results = self.client._handle_response(
            response=response, error_callable=raise_for_vectordb_state_changeset_detail
        )
        return [StateFullSchema.model_validate(result) for result in results]

    def preview_schema_changes(self, integration_name: Optional[str] = None) -> List[str]:
        """
        Preview VectorDB schema changes.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of change descriptions
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/schemas/preview-changes"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        return self.client._handle_response(response=response, error_callable=raise_for_vectordb_state_changeset_detail)

    def is_schema_ready(self, integration_name: Optional[str] = None) -> bool:
        """
        Check if VectorDB schema is ready.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            True if schema is ready, False otherwise
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/schema-ready"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        return self.client._handle_response(response=response, error_callable=raise_for_vectordb_state_changeset_detail)

    def has_schema_changeset(self, integration_name: Optional[str] = None) -> bool:
        """
        Check if VectorDB schema has changeset.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            True if schema has changeset, False otherwise
        """
        url = f"{self.client.base_url}/v1/admin/vector-db/schema-has-changeset"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        return self.client._handle_response(response=response, error_callable=raise_for_vectordb_state_changeset_detail)
