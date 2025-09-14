
from __future__ import annotations
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from config import settings


def get_engine() -> Engine:
    url = f"postgresql+psycopg2://{settings.pg_user}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}"
    return create_engine(url, pool_pre_ping=True)


def upsert_document(engine: Engine, title: str, url: str, language: str, sha256: str) -> int:
    with engine.begin() as conn:
        res = conn.execute(text("""
            INSERT INTO documents (title, source_url, language, sha256)
            VALUES (:title, :url, :language, :sha)
            ON CONFLICT (source_url) DO UPDATE SET language = EXCLUDED.language, sha256 = EXCLUDED.sha256
            RETURNING id
        """), dict(title=title, url=url, language=language, sha=sha256))
        return int(res.scalar())


def insert_chunk(engine: Engine, document_id: int, idx: int, textv: str, lang: str) -> int:
    with engine.begin() as conn:
        res = conn.execute(text("""
            INSERT INTO chunks (document_id, chunk_index, text, lang)
            VALUES (:d, :i, :t, :l)
            RETURNING id
        """), dict(d=document_id, i=idx, t=textv, l=lang))
        return int(res.scalar())


def upsert_indicator(engine: Engine, type_: str, value: str, normalized: Optional[str]) -> int:
    with engine.begin() as conn:
        res = conn.execute(text("""
            INSERT INTO indicators (type, value, normalized_value)
            VALUES (:t, :v, :n)
            ON CONFLICT (type, value) DO UPDATE SET normalized_value = COALESCE(EXCLUDED.normalized_value, indicators.normalized_value)
            RETURNING id
        """), dict(t=type_, v=value, n=normalized))
        return int(res.scalar())


def insert_mention(engine: Engine, indicator_id: int, document_id: int, chunk_id: int, context: str, confidence: float) -> int:
    with engine.begin() as conn:
        res = conn.execute(text("""
            INSERT INTO indicator_mentions (indicator_id, document_id, chunk_id, context, confidence)
            VALUES (:ii, :di, :ci, :ctx, :cf)
            RETURNING id
        """), dict(ii=indicator_id, di=document_id, ci=chunk_id, ctx=context, cf=confidence))
        return int(res.scalar())


def link_relationship(engine: Engine, src_id: int, dst_id: int, relation: str, confidence: float) -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO relationships (src_indicator_id, dst_indicator_id, relation, confidence)
            VALUES (:s, :d, :r, :c)
        """), dict(s=src_id, d=dst_id, r=relation, c=confidence))


def get_indicators_by_type(engine: Engine, type_: str, campaign: Optional[str] = None):
    with engine.begin() as conn:
        if campaign:
            # join via relationships table if PART_OF_CAMPAIGN exists (optional)
            q = text("""
                SELECT DISTINCT i.* FROM indicators i
                JOIN relationships r ON r.src_indicator_id = i.id
                WHERE r.relation = 'PART_OF_CAMPAIGN' AND r.dst_indicator_id IN (
                  SELECT id FROM indicators WHERE type='campaign' AND value=:camp
                ) AND i.type=:t
            """)
            return [dict(row._mapping) for row in conn.execute(q, dict(camp=campaign, t=type_)).fetchall()]
        else:
            q = text("SELECT * FROM indicators WHERE type=:t")
            return [dict(row._mapping) for row in conn.execute(q, dict(t=type_)).fetchall()]


def get_context_for_indicator(engine: Engine, indicator: str):
    with engine.begin() as conn:
        q = text("""
        SELECT i.type, i.value, d.title, d.source_url, c.text as chunk_text, im.confidence
        FROM indicators i
        JOIN indicator_mentions im ON im.indicator_id = i.id
        JOIN chunks c ON c.id = im.chunk_id
        JOIN documents d ON d.id = c.document_id
        WHERE i.value = :val
        ORDER BY im.confidence DESC
        LIMIT 20
        """)
        return [dict(row._mapping) for row in conn.execute(q, dict(val=indicator)).fetchall()]
