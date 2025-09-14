
from __future__ import annotations
from typing import List

# Simple semantic-ish chunking: paragraph split + sliding window

def paragraph_split(text: str) -> List[str]:
    paras = [p.strip() for p in text.split("\n\n")]
    return [p for p in paras if p]


def sliding_window(paras: List[str], window: int = 3, overlap: int = 1) -> List[str]:
    chunks = []
    i = 0
    while i < len(paras):
        w = paras[i:i+window]
        chunks.append("\n\n".join(w))
        if i + window >= len(paras):
            break
        i += max(1, window - overlap)
    return chunks


def make_chunks(text: str, window=3, overlap=1) -> List[str]:
    paras = paragraph_split(text)
    return sliding_window(paras, window, overlap)
