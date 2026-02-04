from pydantic import BaseModel

class IncidentInput(BaseModel):
    message: str
