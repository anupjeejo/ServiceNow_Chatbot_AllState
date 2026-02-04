from backend.app.services.ollama_client import call_ollama

def run(state):
    prompt = f"""
Return ONLY JSON.

Schema:
{{
  "short_description": "",
  "description": "",
  "category": "software|hardware|network|access",
  "priority": "1|2|3|4|5"
}}

Issue:
{state["message"]}
"""
    state["issue"] = call_ollama(prompt)
    return state
