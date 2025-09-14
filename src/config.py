
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # Postgres
    pg_host: str = os.getenv('POSTGRES_HOST', 'localhost')
    pg_port: int = int(os.getenv('POSTGRES_PORT', '5432'))
    pg_db: str = os.getenv('POSTGRES_DB', 'docintel')
    pg_user: str = os.getenv('POSTGRES_USER', 'app')
    pg_password: str = os.getenv('POSTGRES_PASSWORD', 'app_pw')

    # Qdrant
    qdrant_host: str = os.getenv('QDRANT_HOST', 'localhost')
    qdrant_port: int = int(os.getenv('QDRANT_PORT', '6333'))
    qdrant_collection: str = os.getenv('QDRANT_COLLECTION', 'doc_chunks_mmpnet')

    # Neo4j
    neo4j_uri: str = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user: str = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password: str = os.getenv('NEO4J_PASSWORD', 'neo4j_pw')

    # Embeddings
    embed_model: str = os.getenv('EMBED_MODEL', 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    api_host: str = os.getenv('API_HOST', '0.0.0.0')
    api_port: int = int(os.getenv('API_PORT', '8000'))

settings = Settings()
