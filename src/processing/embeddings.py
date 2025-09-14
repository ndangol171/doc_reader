
from __future__ import annotations
from sentence_transformers import SentenceTransformer
from config import settings

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embed_model)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    return model.encode(texts, batch_size=32, normalize_embeddings=True).tolist()
