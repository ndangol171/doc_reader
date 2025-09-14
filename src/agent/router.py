
from __future__ import annotations
# Minimal policy router: decide which backend(s) to use.

def route(query: str) -> dict:
    q = query.lower()
    if any(k in q for k in ["show", "within", "hops", "graph", "network"]):
        return {"use": "graph"}
    if any(k in q for k in ["find", "list", "domains", "urls", "ips", "emails", "phone", "handles", "indicators"]):
        return {"use": "sql"}
    return {"use": "hybrid"}
