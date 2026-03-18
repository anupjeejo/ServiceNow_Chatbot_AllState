from fastapi import APIRouter, HTTPException

from app.core.vector_bootstrap import vector_store
from app.graph.workflow import workflow
from app.schemas.request import IncidentInput, IncidentKBDocumentInput, IncidentQueryInput
from app.schemas.response import AIResponse, IncidentKBSaveResponse, IncidentQueryResponse
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

        kb_results = vector_store.search(
            req.question,
            k=5,
            filters={
                "source": "kb",
            },
        )

        kb_sections = [item.get("text", "").strip() for item in kb_results if item.get("text", "").strip()]
        kb_references = sorted(
            {
                item.get("kb_name", "").strip()
                for item in kb_results
                if item.get("kb_name", "").strip()
            }
        )
        if req.kb_document and req.kb_document.strip():
            kb_sections.append(req.kb_document.strip())

        kb_section = (
            "\n\n---\n\n".join(kb_sections)
            if kb_sections
            else "No KB document was provided."
        )

        prompt = f"""
You are an IT support incident assistant.
Answer the user question strictly based on the incident details and KB document below.
If the answer is not available in the provided details, say clearly that the incident and KB data do not include that information.
If the user asks about root cause, RCA steps, or investigation approach, use KB details when present and tie guidance back to this incident.
Keep the answer concise and useful.

Incident Details:
- Number: {incident['number']}
- Short description: {incident['short_description']}
- Description: {incident['description']}
- Resolution notes: {incident['close_notes']}
- State: {incident['state']}
- Assignment Group: {incident['assignment_group']}

KB Document:
{kb_section}

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
            "kb_references": kb_references if kb_references else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kb-document", response_model=IncidentKBSaveResponse)
def save_incident_kb(req: IncidentKBDocumentInput):
    kb_document = req.kb_document.strip()
    kb_name = (req.kb_name or "").strip() or "General KB Document"

    if not kb_document:
        raise HTTPException(status_code=400, detail="KB document content is required.")

    vector_store.upsert_by_key(
        key=f"kb::{kb_name.lower()}",
        text=kb_document,
        metadata={
            "source": "kb",
            "kb_name": kb_name,
        },
    )

    return {
        "kb_name": kb_name,
        "message": "KB document saved to vector store.",
    }
