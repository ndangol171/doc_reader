
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id SERIAL PRIMARY KEY,
  title TEXT,
  source_url TEXT UNIQUE,
  language TEXT,
  published_at TIMESTAMP NULL,
  sha256 TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
  id SERIAL PRIMARY KEY,
  document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER,
  text TEXT,
  lang TEXT,
  sha1 TEXT
);

CREATE TABLE IF NOT EXISTS indicators (
  id SERIAL PRIMARY KEY,
  type TEXT NOT NULL,
  value TEXT NOT NULL,
  normalized_value TEXT,
  first_seen TIMESTAMP,
  last_seen TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS indicators_unique ON indicators(type, value);

CREATE TABLE IF NOT EXISTS indicator_mentions (
  id SERIAL PRIMARY KEY,
  indicator_id INTEGER REFERENCES indicators(id) ON DELETE CASCADE,
  document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
  chunk_id INTEGER REFERENCES chunks(id) ON DELETE CASCADE,
  context TEXT,
  confidence REAL,
  ts TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS relationships (
  id SERIAL PRIMARY KEY,
  src_indicator_id INTEGER REFERENCES indicators(id) ON DELETE CASCADE,
  dst_indicator_id INTEGER REFERENCES indicators(id) ON DELETE CASCADE,
  relation TEXT,
  confidence REAL,
  ts TIMESTAMP DEFAULT NOW()
);
