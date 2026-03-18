from pydantic import BaseModel


class IncidentInput(BaseModel):
    message: str


class IncidentQueryInput(BaseModel):
    incident_number: str
    question: str
    kb_document: str | None = None


class IncidentKBDocumentInput(BaseModel):
    kb_name: str | None = None
    kb_document: str
