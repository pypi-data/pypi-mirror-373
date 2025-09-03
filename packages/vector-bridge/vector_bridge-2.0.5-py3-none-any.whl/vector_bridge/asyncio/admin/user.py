from typing import Optional

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.user import raise_for_user_detail
from vector_bridge.schema.user import (User, UsersList, UserUpdate,
                                       UserWithIntegrations)


class AsyncUserAdmin:
    """Async admin client for user management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def get_me(self) -> UserWithIntegrations:
        """
        Retrieve information about the currently authenticated user.

        Returns:
            User information including integrations
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/me"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
            return UserWithIntegrations.model_validate(data)

    async def get_users_in_my_organization(
        self, limit: int = 25, last_evaluated_key: Optional[str] = None
    ) -> UsersList:
        """
        Retrieve information about the users of the authenticated user's organization.

        Args:
            limit: Number of users to return
            last_evaluated_key: Last evaluated key for pagination

        Returns:
            UsersList with users and pagination information
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/users/my-organization"
        params = {"limit": limit}
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
            return UsersList.model_validate(result)

    async def update_me(self, user_data: UserUpdate) -> User:
        """
        Update details of the currently authenticated user.

        Args:
            user_data: Dictionary containing user fields to update

        Returns:
            Updated user information
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/update/me"
        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, json=user_data.model_dump()) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
            return User.model_validate(data)

    async def change_password(self, old_password: str, new_password: str) -> User:
        """
        Change password of the currently authenticated user.

        Args:
            old_password: Current password
            new_password: New password

        Returns:
            Updated user information
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/change-password/me"
        data = {"old_password": old_password, "new_password": new_password}
        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, json=data) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
            return User.model_validate(data)

    async def disable_me(self) -> None:
        """
        Disable the account of the currently authenticated user.
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/disable/me"
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_user_detail)

    async def add_user(self, email: str, first_name: str = "", last_name: str = "", password: str = "") -> User:
        """
        Add a new agent user.

        Args:
            email: The email of the user
            first_name: The first name of the user
            last_name: The last name of the user
            password: The password of the user

        Returns:
            Created user information
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/add-agent"
        params = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
            return User.model_validate(data)

    async def remove_user(self, user_id: str) -> None:
        """
        Remove an agent user.

        Args:
            user_id: The user to be removed

        Returns:
            None
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/remove-agent/{user_id}"
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_user_detail)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve user information based on their unique user ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            User information or None if not found
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/id/{user_id}"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
            return User.model_validate(data) if data else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve user information based on their email address.

        Args:
            email: The email address of the user

        Returns:
            User information or None if not found
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/email/{email}"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
            return User.model_validate(data) if data else None

    async def disable_user(self, user_id: str) -> None:
        """
        Disable a user account, identified by their unique user ID.

        Args:
            user_id: The unique identifier of the user whose account is to be disabled
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/user/disable/{user_id}"
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_user_detail)
