import re


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = text.strip().lower()
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    cleaned = re.sub(r"https?://\S+|www\.\S+", " url ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()
