import requests
from backend.app.core.config import settings
from backend.app.utils.json_sanitizer import extract_json

def call_ollama(prompt: str) -> dict:
    r = requests.post(
        settings.OLLAMA_URL,
        json={"model": "gemma3:4b", "prompt": prompt, "stream": False},
        timeout=60
    )
    raw = r.json()["response"]
    print("OLLAMA RAW >>>", raw)

    if r.status_code != 200:
        raise RuntimeError("Ollama request failed")

    return extract_json(raw)
