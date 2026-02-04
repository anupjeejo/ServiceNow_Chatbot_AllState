from fastapi import FastAPI
from backend.app.api.routes import router
from backend.app.core.config import settings
from backend.app.core.vector_bootstrap import initialize_vector_store

app = FastAPI(title="ServiceNow AI Agent")

app.include_router(router)

@app.on_event("startup")
def startup():
    initialize_vector_store()
@app.get("/health")
def health():
    return {"status": "ok"}

