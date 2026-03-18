from pathlib import Path

from app.services.vector_store import VectorStore
from app.services.servicenow_client import get_closed_incidents_for_index

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VECTOR_DB_DIR = PROJECT_ROOT / "backend" / "data" / "vector_store"

vector_store = VectorStore(storage_dir=VECTOR_DB_DIR)

def initialize_vector_store():
    try:
        incidents = get_closed_incidents_for_index()
        for incident in incidents:
            vector_store.upsert_by_key(
                key=f"incident::{incident['number']}",
                text=incident["text"],
                metadata={
                    "source": "incident",
                    "incident_number": incident["number"],
                    "number": incident["number"],
                    "resolution": incident["text"],
                    "assignment_group": incident.get("assignment_group"),
                },
            )

    except Exception as e:
        print("⚠️ Vector store not initialized:", str(e))
