
from __future__ import annotations
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from config import settings

client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def ensure_collection(dim: int = 768):
    if settings.qdrant_collection not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )


def upsert_points(vectors: list[list[float]], payloads: list[dict]):
    points = [PointStruct(id=i, vector=vectors[i], payload=payloads[i]) for i in range(len(vectors))]
    client.upsert(collection_name=settings.qdrant_collection, points=points)


def search(query_vec: list[float], top_k: int = 10, filter_payload: dict | None = None):
    flt = None
    if filter_payload:
        conditions = []
        for k, v in filter_payload.items():
            conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
        flt = Filter(must=conditions)
    return client.search(collection_name=settings.qdrant_collection, query_vector=query_vec, limit=top_k, query_filter=flt)
