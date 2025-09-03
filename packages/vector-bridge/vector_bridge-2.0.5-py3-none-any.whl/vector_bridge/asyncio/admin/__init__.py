from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.asyncio.admin.ai_knowledge import AsyncAIKnowledgeAdmin
from vector_bridge.asyncio.admin.api_keys import AsyncAPIKeysAdmin
from vector_bridge.asyncio.admin.chat import AsyncChatAdmin
from vector_bridge.asyncio.admin.functions import AsyncFunctionsAdmin
from vector_bridge.asyncio.admin.instructions import AsyncInstructionsAdmin
from vector_bridge.asyncio.admin.integrations import AsyncIntegrationsAdmin
from vector_bridge.asyncio.admin.logs import AsyncLogsAdmin
from vector_bridge.asyncio.admin.message import AsyncMessageAdmin
from vector_bridge.asyncio.admin.notifications import AsyncNotificationsAdmin
from vector_bridge.asyncio.admin.organization import AsyncOrganizationAdmin
from vector_bridge.asyncio.admin.security_groups import \
    AsyncSecurityGroupsAdmin
from vector_bridge.asyncio.admin.settings import AsyncSettingsAdmin
from vector_bridge.asyncio.admin.tasks import AsyncTasksAdmin
from vector_bridge.asyncio.admin.usage import AsyncUsageAdmin
from vector_bridge.asyncio.admin.user import AsyncUserAdmin
from vector_bridge.asyncio.admin.vector_db import AsyncVectorDBAdmin
from vector_bridge.asyncio.admin.workflows import AsyncWorkflowsAdmin


class AsyncAdminClient:
    """Async admin client providing access to all admin endpoints that require authentication."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

        # Initialize async admin subclients
        self.settings = AsyncSettingsAdmin(client)
        self.logs = AsyncLogsAdmin(client)
        self.notifications = AsyncNotificationsAdmin(client)
        self.usage = AsyncUsageAdmin(client)
        self.user = AsyncUserAdmin(client)
        self.organization = AsyncOrganizationAdmin(client)
        self.security_groups = AsyncSecurityGroupsAdmin(client)
        self.integrations = AsyncIntegrationsAdmin(client)
        self.instructions = AsyncInstructionsAdmin(client)
        self.functions = AsyncFunctionsAdmin(client)
        self.workflows = AsyncWorkflowsAdmin(client)
        self.api_keys = AsyncAPIKeysAdmin(client)
        self.chat = AsyncChatAdmin(client)
        self.message = AsyncMessageAdmin(client)
        self.ai_knowledge = AsyncAIKnowledgeAdmin(client)
        self.vector_db = AsyncVectorDBAdmin(client)
        self.tasks = AsyncTasksAdmin(client)
