
.PHONY: up down ingest api test
up:
	docker compose up -d

down:
	docker compose down -v

init_db:
	docker compose exec postgres psql -U app -d docintel -f /docker-entrypoint-initdb.d/init_db.sql
	docker compose exec neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} -f /init/init_neo4j.cql

pipeline:
	docker compose run --rm worker python -m pipeline.run_pipeline

api:
	docker compose up -d api

test:
	pytest -q
