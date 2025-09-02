from typing import Optional
from uuid import UUID

from weaviate.collections.classes.filters import _Filters
from weaviate.collections.classes.grpc import _Sorting

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.queries import raise_for_query_detail
from vector_bridge.schema.queries import Query, QueryResponse


class QueryClient:
    """User client for query endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def run_search_query(
        self,
        vector_schema: str,
        integration_name: str = None,
        near_text: Optional[str] = None,
        filters: Optional[_Filters] = None,
        sort: Optional[_Sorting] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs,
    ) -> QueryResponse:
        """
        Run a vector search query.

        Args:
            vector_schema: The schema to be queried
            integration_name: The name of the Integration
            near_text: The query text
            filters: The filters to apply to the query
            sort: The sort to apply to the query
            limit: The maximum number of results to return
            offset: The offset to start with

        Returns:
            Search results
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        query_payload = Query(
            query=near_text,
            filters=filters,
            sort=sort,
            limit=limit,
            offset=offset,
            kwargs=kwargs,
        )

        url = f"{self.client.base_url}/v1/vector-query/search/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}

        headers = self.client._get_auth_headers()

        response = self.client.session.post(url, headers=headers, params=params, json=query_payload.serialize_bytes())
        result = self.client._handle_response(response=response, error_callable=raise_for_query_detail)
        return QueryResponse.model_validate(result)

    def run_find_similar_query(
        self,
        vector_schema: str,
        near_id: UUID,
        integration_name: str = None,
        filters: Optional[_Filters] = None,
        sort: Optional[_Sorting] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs,
    ) -> QueryResponse:
        """
        Run a vector similarity query.

        Args:
            vector_schema: The schema to be queried
            near_id: The id from which to find similar documents
            integration_name: The name of the Integration
            filters: The filters to apply to the query
            sort: The sort to apply to the query
            limit: The maximum number of results to return
            offset: The offset to start with
        Returns:
            Search results
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        query_payload = Query(
            near_id=near_id,
            filters=filters,
            sort=sort,
            limit=limit,
            offset=offset,
            kwargs=kwargs,
        )

        url = f"{self.client.base_url}/v1/vector-query/find-similar/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}

        headers = self.client._get_auth_headers()

        response = self.client.session.post(url, headers=headers, params=params, json=query_payload.serialize_bytes())
        result = self.client._handle_response(response=response, error_callable=raise_for_query_detail)
        return QueryResponse.model_validate(result)
