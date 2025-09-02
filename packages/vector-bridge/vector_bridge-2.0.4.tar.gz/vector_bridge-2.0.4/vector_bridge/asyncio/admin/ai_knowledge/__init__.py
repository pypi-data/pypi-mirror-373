from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.asyncio.admin.ai_knowledge.database import \
    AsyncDatabaseAIKnowledgeAdmin
from vector_bridge.asyncio.admin.ai_knowledge.file_storage import \
    AsyncFileStorageAIKnowledgeAdmin


class AsyncAIKnowledgeAdmin:
    """Async admin client for AI Knowledge management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client
        self.file_storage = AsyncFileStorageAIKnowledgeAdmin(client)
        self.database = AsyncDatabaseAIKnowledgeAdmin(client)
