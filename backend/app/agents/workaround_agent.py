from backend.app.services.ollama_client import call_ollama

def run(state):
    if not state.get("historical"):
        state["workaround"] = {
            "workaround": "No similar historical incidents found. Proceed with standard troubleshooting.",
            "confidence": "low"
        }
        return state

    incidents = "\n".join(
        f"{i['number']}: {i['resolution']}" for i in state["historical"]
    )

    prompt = f"""
You are a Tier-2 IT support engineer.

Use ONLY the incidents below.
Do NOT add explanations.
Return ONLY valid JSON.

Schema:
{{
  "workaround": "string",
  "confidence": "high|medium|low"
}}

Incidents:
{incidents}
"""

    try:
        state["workaround"] = call_ollama(prompt)
    except Exception:
        # Safety net – NEVER crash workflow
        state["workaround"] = {
            "workaround": "Unable to generate workaround from historical data.",
            "confidence": "low"
        }

    return state
