from fastapi import APIRouter, HTTPException
from backend.app.schemas.request import IncidentInput
from backend.app.schemas.response import AIResponse
from backend.app.graph.workflow import workflow
from backend.app.services.servicenow_client import create_incident

router = APIRouter()

@router.post("/chat", response_model=AIResponse)
def chat(req: IncidentInput):
    try:
        state = workflow.invoke({"message": req.message})
        print("STATE >>>", state)  # DEBUG

        ticket = create_incident(
            state["issue"],
            state["assignment_group"]
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
        traceback.print_exc()      # 🔥 THIS SHOWS ROOT CAUSE
        raise HTTPException(status_code=500, detail=str(e))