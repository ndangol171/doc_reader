
# Document Intelligence Pipeline (AI-Focused Threat Intel)

**Goal:** Build a pipeline that ingests PDF threat reports, extracts indicators (IOCs + social handles + trackers), creates multilingual embeddings for semantic retrieval, stores relationships in a graph, and serves a RAG API with hybrid search and graph traversal.

> **Assumptions**
> * Hybrid architecture (PostgreSQL + pgvector / Qdrant for vectors, Neo4j for relationships)
> * Multilingual embeddings using `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
> * PDF parsing with PyMuPDF (layout-aware blocks) and basic table capture
> * LangGraph router to decide between vector, SQL, and graph backends


## Services (Docker Compose)
- **PostgreSQL** (+ `pgvector` installed but we store vectors in **Qdrant** to simplify)
- **Qdrant** vector DB
- **Neo4j** for graph relations
- **API** (FastAPI + LangGraph)
- **Worker** (ingestion + processing)

---

## Quickstart

1. **Configure**
   ```bash
   cp .env.sample .env
   # edit credentials if needed
   ```

2. **Start infra**
   ```bash
   docker compose up -d
   ```

3. **Initialize DBs** (one-time)
   ```bash
   docker compose exec postgres psql -U app -d docintel -f /docker-entrypoint-initdb.d/init_db.sql
   docker compose exec neo4j cypher-shell -u neo4j -p $NEO4J_PASSWORD -f /init/init_neo4j.cql
   ```

4. **Run ingestion pipeline** (downloads and processes the 3 PDFs)
   ```bash
   docker compose run --rm worker python -m pipeline.run_pipeline
   ```

5. **Run API**
   ```bash
   # API is already running if service 'api' is up; otherwise
   docker compose up -d api
   # Open http://localhost:8000/docs
   ```

6. **Try queries**
   ```bash
   # Semantic
   curl -s "http://localhost:8000/search?q=What Russian disinformation campaigns target France?" | jq

   # Indicator lookup
   curl -s "http://localhost:8000/indicators/domain?campaign=Doppelgänger" | jq

   # Context for an indicator
   curl -s "http://localhost:8000/context/example.com" | jq

   # Graph traversal (2 hops)
   curl -s "http://localhost:8000/relationships/example.com?hops=2" | jq

   # Network data (bonus)
   curl -s "http://localhost:8000/network/example.com" | jq
   ```

---

## Data Model (Relational + Graph)

### PostgreSQL
- `documents(id, title, source_url, language, published_at, sha256)`
- `chunks(id, document_id, chunk_index, text, lang, sha1)`
- `indicators(id, type, value, normalized_value, first_seen, last_seen)`
- `indicator_mentions(id, indicator_id, document_id, chunk_id, context, confidence, ts)`
- `relationships(id, src_indicator_id, dst_indicator_id, relation, confidence, ts)`

### Neo4j
- Nodes: `Indicator {value, type}`, `Document {title, url}`, `Campaign {name}`
- Edges: `MENTIONED_IN`, `RELATED_TO`, `PART_OF_CAMPAIGN`

### Vector Store (Qdrant)
- Collection `doc_chunks_mmpnet`: 768-dim vectors; payload: `doc_id`, `chunk_id`, `lang`, `campaign`

---

