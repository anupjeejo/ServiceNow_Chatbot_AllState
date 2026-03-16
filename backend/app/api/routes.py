from fastapi import APIRouter, HTTPException

from app.graph.workflow import workflow
from app.schemas.request import IncidentInput, IncidentQueryInput
from app.schemas.response import AIResponse, IncidentQueryResponse
from app.services.ollama_client import call_ollama
from app.services.servicenow_client import create_incident, get_incident_by_number

router = APIRouter()


@router.post("/chat", response_model=AIResponse)
def chat(req: IncidentInput):
    try:
        state = workflow.invoke({"message": req.message})
        print("STATE >>>", state)  # DEBUG

        ticket = create_incident(
            state["issue"],
            state["assignment_group"],
            state["workaround"]["workaround"],
        )

        return {
            "ticket_number": ticket,
            "summary": state["summary"],
            "workaround": state["workaround"]["workaround"],
            "confidence": state["workaround"]["confidence"],
            "based_on_incidents": [i["number"] for i in state["historical"]],
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incident-query", response_model=IncidentQueryResponse)
def incident_query(req: IncidentQueryInput):
    try:
        incident = get_incident_by_number(req.incident_number.strip())
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {req.incident_number} not found")

        prompt = f"""
You are an IT support incident assistant.
Answer the user question strictly based on the incident details below.
If the answer is not available in the details, say clearly that the incident data does not include that information.
Keep the answer concise and useful.

Incident Details:
- Number: {incident['number']}
- Short description: {incident['short_description']}
- Description: {incident['description']}
- Resolution notes: {incident['close_notes']}
- State: {incident['state']}
- Assignment Group: {incident['assignment_group']}

User Question:
{req.question}

Return JSON only in this schema:
{{
  "answer": "string"
}}
"""

        result = call_ollama(prompt)
        answer = result.get("answer") if isinstance(result, dict) else None

        return {
            "incident_number": incident["number"],
            "answer": answer or "I could not generate a reliable answer from the incident details.",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
