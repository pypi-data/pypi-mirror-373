import inspect
import json
from collections import defaultdict
from typing import Callable, Dict, List, Optional

from redis.asyncio import Redis

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.notifications import \
    raise_for_notification_detail
from vector_bridge.schema.notifications import (NotificationsList,
                                                NotificationState)


class AsyncNotificationsAdmin:
    """Async admin client for notifications endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient, redis_url: str = None):
        self.client = client
        self.listener = AsyncNotificationListener(
            redis_url=redis_url or self.client.redis_url,
        )

    async def list_notifications(
        self,
        integration_name: str = None,
        limit: int = 25,
        last_evaluated_key: Optional[str] = None,
    ) -> NotificationsList:
        """
        List notifications.

        Args:
            integration_name: The name of the Integration
            limit: Number of notifications to return
            last_evaluated_key: Last evaluated key for pagination

        Returns:
            NotificationsList with notifications and pagination information
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/notifications"
        params = {"integration_name": integration_name, "limit": limit}
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_notification_detail)
            return NotificationsList.model_validate(result)

    async def push_notification(
        self,
        payload: dict,
        integration_name: str = None,
        channel: str = "default",
    ) -> NotificationState:
        """
        Send a notification to Redis Pub/Sub. It will not be stored

        Args:
            payload: Notification payload to send
            integration_name: The name of the Integration
            channel: Notification channel (default: "default")

        Returns:
            dict with status and channel information
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/notifications/send"
        params = {
            "integration_name": integration_name,
            "channel": channel,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=payload) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_notification_detail)
            return NotificationState.model_validate(result)


class AsyncNotificationListener:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.channel_handlers: Dict[str, List[Callable]] = defaultdict(list)

    def on(self, channel: str):
        """Decorator to register an async handler for a Redis channel."""

        def decorator(func: Callable):
            self.channel_handlers[channel].append(func)
            return func

        return decorator

    async def _dispatch(self, channel: str, message: str):
        try:
            payload = json.loads(message)
        except Exception:
            payload = message

        for handler in self.channel_handlers.get(channel, []):
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                print(f"❌ Error in handler for {channel}: {e}")

    async def listen(self):
        channels = list(self.channel_handlers.keys())
        if not channels:
            raise RuntimeError("No channels registered. Use @on(channel).")

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(*channels)
        print(f"🔌 Async listening on channels: {channels}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await self._dispatch(message["channel"], message["data"])
        finally:
            await pubsub.close()
