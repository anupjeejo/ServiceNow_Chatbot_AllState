from typing import List

from pydantic import BaseModel


class AIResponse(BaseModel):
    ticket_number: str
    summary: str
    workaround: str
    confidence: str
    based_on_incidents: List[str]


class IncidentQueryResponse(BaseModel):
    incident_number: str
    answer: str
    kb_references: List[str] | None = None


class IncidentKBSaveResponse(BaseModel):
    kb_name: str
    message: str
