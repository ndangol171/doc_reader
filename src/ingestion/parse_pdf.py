
from __future__ import annotations
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict
from utils.text import clean_text


def parse_pdf(path: Path) -> Dict:
    doc = fitz.open(path)
    pages = []
    for p in doc:
        blocks = p.get_text("dict")["blocks"]
        texts = []
        for b in blocks:
            if b.get("type") == 0:
                # concatenate lines inside each block
                lines = []
                for l in b.get("lines", []):
                    span_text = " ".join([s.get("text", "") for s in l.get("spans", [])])
                    lines.append(span_text)
                block_text = clean_text(" ".join(lines))
                if block_text:
                    texts.append(block_text)
        page_text = clean_text("\n".join(texts))
        pages.append(page_text)
    return {"pages": pages, "text": "\n\n".join(pages)}
