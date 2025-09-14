
from fastapi import FastAPI, Query
from typing import Optional
from storage.vectorstore import search as vs_search
from processing.embeddings import embed_texts
from storage.postgres import get_engine, get_indicators_by_type, get_context_for_indicator
from storage.neo4j import k_hop_neighbors
from agent.router import route

app = FastAPI(title="DocIntel RAG API")

engine = get_engine()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/search")
async def search(q: str = Query(...), top_k: int = 8):
    plan = route(q)
    vec = embed_texts([q])[0]
    hits = vs_search(vec, top_k=top_k)
    payloads = [h.payload for h in hits]
    return {"plan": plan, "results": payloads}

@app.get("/indicators/{type}")
async def indicators_by_type(type: str, campaign: Optional[str] = None):
    data = get_indicators_by_type(engine, type, campaign)
    return data

@app.get("/context/{indicator}")
async def indicator_context(indicator: str):
    ctx = get_context_for_indicator(engine, indicator)
    return ctx

@app.get("/relationships/{indicator}")
async def relationships(indicator: str, hops: int = 2):
    graph = k_hop_neighbors(indicator, hops)
    return graph

@app.get("/network/{indicator}")
async def network(indicator: str, hops: int = 2):
    graph = k_hop_neighbors(indicator, hops)
    return graph
