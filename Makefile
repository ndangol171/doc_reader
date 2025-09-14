
.PHONY: up down ingest api test
up:
	docker compose up -d

down:
	docker compose down -v

ingest:
	docker compose run --rm worker python -m pipeline.run_pipeline

api:
	docker compose up -d api

test:
	pytest -q
