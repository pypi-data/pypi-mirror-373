from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.asyncio.admin.vector_db.changeset import \
    AsyncVectorDBChangesetAdmin
from vector_bridge.asyncio.admin.vector_db.state import AsyncVectorDBStateAdmin


class AsyncVectorDBAdmin:
    """Async admin client for VectorDB management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client
        self.changeset = AsyncVectorDBChangesetAdmin(client)
        self.state = AsyncVectorDBStateAdmin(client)
