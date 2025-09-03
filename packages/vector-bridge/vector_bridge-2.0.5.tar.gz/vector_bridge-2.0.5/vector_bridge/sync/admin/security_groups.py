from typing import Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.security_groups import \
    raise_for_security_group_detail
from vector_bridge.schema.security_group import (PaginatedSecurityGroups,
                                                 SecurityGroup,
                                                 SecurityGroupCreate,
                                                 SecurityGroupUpdate)


class SecurityGroupsAdmin:
    """Admin client for security group management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def create_security_group(self, security_group_data: SecurityGroupCreate) -> SecurityGroup:
        """
        Create a new security group.

        Args:
            organization_id: The ID of the organization
            security_group_data: Details of the security group to create

        Returns:
            Created security group
        """
        url = f"{self.client.base_url}/v1/admin/security-group/create"
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, json=security_group_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_security_group_detail)
        return SecurityGroup.model_validate(result)

    def update_security_group(self, group_id: str, security_group_data: SecurityGroupUpdate) -> SecurityGroup:
        """
        Update an existing security group by ID.

        Args:
            group_id: The Security Group ID
            security_group_data: Updated details for the security group

        Returns:
            Updated security group
        """
        url = f"{self.client.base_url}/v1/admin/security-group/{group_id}/update"
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, json=security_group_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_security_group_detail)
        return SecurityGroup.model_validate(result)

    def get_security_group(self, group_id: str) -> Optional[SecurityGroup]:
        """
        Retrieve details of a specific security group by ID.

        Args:
            group_id: The Security Group ID

        Returns:
            Security group details
        """
        url = f"{self.client.base_url}/v1/admin/security-group/{group_id}"
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers)
        result = self.client._handle_response(response=response, error_callable=raise_for_security_group_detail)
        return SecurityGroup.model_validate(result) if result else None

    def list_security_groups(
        self,
        limit: int = 10,
        last_evaluated_key: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> PaginatedSecurityGroups:
        """
        Retrieve a paginated list of all security groups for the organization.

        Args:
            limit: Number of items per page
            last_evaluated_key: Key to continue pagination from
            sort_by: The sort field

        Returns:
            PaginatedSecurityGroups with security groups and pagination information
        """
        url = f"{self.client.base_url}/v1/admin/security-groups"
        params = {"limit": limit, "sort_by": sort_by}
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_security_group_detail)
        return PaginatedSecurityGroups.model_validate(result)

    def delete_security_group(self, group_id: str) -> None:
        """
        Delete a specific security group by ID.

        Args:
            group_id: The Security Group ID
        """
        url = f"{self.client.base_url}/v1/admin/security-group/{group_id}/delete"
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers)
        if response.status_code != 204:
            self.client._handle_response(response=response, error_callable=raise_for_security_group_detail)
