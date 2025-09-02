from typing import Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.logs import raise_for_log_detail
from vector_bridge.schema.logs import PaginatedLogs


class LogsAdmin:
    """Admin client for logs endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def list_logs(
        self,
        integration_name: str = None,
        limit: int = 25,
        last_evaluated_key: Optional[str] = None,
        filter_key: Optional[str] = None,
        filter_value: Optional[str] = None,
    ) -> PaginatedLogs:
        """
        List logs with optional filters and pagination.

        Args:
            integration_name: The name of the Integration
            limit: Number of logs to return
            last_evaluated_key: Last evaluated key for pagination
            filter_key: Logs Filter (USER or API_KEY_HASH)
            filter_value: Filter logs by user ID or API key hash

        Returns:
            PaginatedLogs with logs and pagination information
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/logs"
        params = {"integration_name": integration_name, "limit": limit}
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key
        if filter_key:
            params["filter_key"] = filter_key
        if filter_value:
            params["filter_value"] = filter_value

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_log_detail)
        return PaginatedLogs.model_validate(result)
