from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.core.vector_bootstrap import initialize_vector_store

app = FastAPI(title="ServiceNow AI Agent")

app.include_router(router)

@app.on_event("startup")
def startup():
    initialize_vector_store()
@app.get("/health")
def health():
    return {"status": "ok"}

