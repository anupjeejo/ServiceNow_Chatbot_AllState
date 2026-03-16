from pydantic import BaseModel


class IncidentInput(BaseModel):
    message: str


class IncidentQueryInput(BaseModel):
    incident_number: str
    question: str
