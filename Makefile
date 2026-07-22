.PHONY: dev test lint clean docker-up docker-build

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

cov:
	pytest --cov=app --cov-report=term-missing --cov-report=xml

lint:
	ruff check .
	ruff format --check .

clean:
	rm -rf __pycache__ .pytest_cache .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docker-build:
	docker compose build

docker-up:
	docker compose up -d
