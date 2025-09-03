from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.organization import \
    raise_for_organization_detail
from vector_bridge.schema.organization import Organization


class OrganizationAdmin:
    """Admin client for organization management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def get_my_organization(self) -> Organization:
        """
        Retrieve detailed information about the organization linked to the currently authenticated user's account.

        Returns:
            Organization details
        """
        url = f"{self.client.base_url}/v1/admin/organization/me"
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers)
        data = self.client._handle_response(response=response, error_callable=raise_for_organization_detail)
        return Organization.model_validate(data)
