def redact_pii(text: str) -> str:
    return text.replace("@", "[at]")
