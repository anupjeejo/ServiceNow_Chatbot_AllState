from backend.app.services.vector_store import VectorStore
from backend.app.services.servicenow_client import get_closed_incidents_for_index

vector_store = VectorStore()

def initialize_vector_store():
    try:
        incidents = get_closed_incidents_for_index()
        texts = [i["text"] for i in incidents]
        metadata = incidents

        if texts:
            vector_store.build(texts, metadata)

    except Exception as e:
        print("⚠️ Vector store not initialized:", str(e))
