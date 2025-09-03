import json
import threading
from collections import defaultdict
from typing import Callable, Dict, List, Optional

import redis

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.notifications import \
    raise_for_notification_detail
from vector_bridge.schema.notifications import (NotificationsList,
                                                NotificationState)


class NotificationsAdmin:
    """Admin client for notifications endpoints."""

    def __init__(self, client: VectorBridgeClient, redis_url: str = None):
        self.client = client
        self.listener = NotificationListener(
            redis_url=redis_url or self.client.redis_url,
        )

    def list_notifications(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/notifications"
        params = {"integration_name": integration_name, "limit": limit}
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_notification_detail)
        return NotificationsList.model_validate(result)

    def push_notification(
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
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/notifications/send"
        params = {
            "integration_name": integration_name,
            "channel": channel,
        }
        headers = self.client._get_auth_headers()

        response = self.client.session.post(url, headers=headers, params=params, json=payload)
        result = self.client._handle_response(response=response, error_callable=raise_for_notification_detail)
        return NotificationState.model_validate(result)


class NotificationListener:
    def __init__(self, redis_url: str):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.channel_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._pubsub = self.redis.pubsub()
        self._thread = None

    def on(self, channel: str):
        """Decorator to register a handler for a Redis channel."""

        def decorator(func: Callable):
            self.channel_handlers[channel].append(func)
            return func

        return decorator

    def _dispatch(self, channel: str, message: str):
        try:
            payload = json.loads(message)
        except Exception:
            payload = message

        for handler in self.channel_handlers.get(channel, []):
            try:
                handler(payload)
            except Exception as e:
                print(f"❌ Error in handler for {channel}: {e}")

    def listen(self):
        channels = list(self.channel_handlers.keys())
        if not channels:
            raise RuntimeError("No channels registered. Use @on(channel).")

        self._pubsub.subscribe(*channels)
        print(f"🔌 Listening on channels: {channels}")

        def run():
            for message in self._pubsub.listen():
                if message["type"] == "message":
                    self._dispatch(message["channel"], message["data"])

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
