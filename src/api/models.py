
from pydantic import BaseModel
from typing import List, Dict, Any

class SearchQuery(BaseModel):
    q: str
    top_k: int = 8

class NetworkResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
