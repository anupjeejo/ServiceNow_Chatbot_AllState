from backend.app.services.ollama_client import call_ollama

def run(state):
    if not state.get("historical"):
        state["summary"] = "No historical data available to summarize."
        return state

    prompt = f"""
Summarize common root cause in 3 lines.
Return JSON: {{ "summary": "" }}

Data:
{state["historical"]}
"""
    result = call_ollama(prompt)
    state["summary"] = result.get("summary", "No summary available.")
    return state
