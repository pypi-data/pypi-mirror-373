from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.settings import raise_for_setting_detail
from vector_bridge.schema.settings import Settings


class AsyncSettingsAdmin:
    """Async admin client for settings endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def get_settings(self) -> Settings:
        """Get system settings."""
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/settings"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_setting_detail)
            return Settings.model_validate(result)
