from pydantic import BaseModel
from typing import List

class AIResponse(BaseModel):
    ticket_number: str
    summary: str
    workaround: str
    confidence: str
    based_on_incidents: List[str]
