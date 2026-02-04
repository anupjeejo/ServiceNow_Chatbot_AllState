import json
import re

def extract_json(text: str) -> dict:
    """
    Extract JSON from LLM output.
    Handles:
    - ```json { ... } ```
    - Extra text before/after JSON
    - Multiple JSON blocks (takes first valid)
    """

    # 1. Remove markdown code fences but KEEP content
    text = text.strip()
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    # 2. Find JSON objects
    matches = re.findall(r"\{[\s\S]*?\}", text)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    raise ValueError("No valid JSON object found in LLM output")
