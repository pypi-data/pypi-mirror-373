from vector_bridge import VectorBridgeClient
from vector_bridge.sync.admin.vector_db.changeset import VectorDBChangesetAdmin
from vector_bridge.sync.admin.vector_db.state import VectorDBStateAdmin


class VectorDBAdmin:
    """Admin client for VectorDB management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client
        self.changeset = VectorDBChangesetAdmin(client)
        self.state = VectorDBStateAdmin(client)
