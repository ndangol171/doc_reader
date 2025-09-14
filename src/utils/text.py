
import re
from langdetect import detect

WS_RE = re.compile(r"\s+")

def clean_text(s: str) -> str:
    s = s.replace("\u00A0", " ")  # nbsp
    s = WS_RE.sub(" ", s)
    return s.strip()

def detect_lang(s: str) -> str:
    try:
        return detect(s)
    except Exception:
        return 'unknown'
