from vector_bridge import VectorBridgeClient
from vector_bridge.sync.admin.ai_knowledge.database import \
    DatabaseAIKnowledgeAdmin
from vector_bridge.sync.admin.ai_knowledge.file_storage import \
    FileStorageAIKnowledgeAdmin


class AIKnowledgeAdmin:
    """Admin client for AI Knowledge management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client
        self.file_storage = FileStorageAIKnowledgeAdmin(client)
        self.database = DatabaseAIKnowledgeAdmin(client)
