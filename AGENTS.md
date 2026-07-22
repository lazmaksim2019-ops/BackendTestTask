# Project: Backend Developer Landing API

## Tech Stack
- Python 3.11+
- FastAPI (async)
- Pydantic v2 for validation
- Jinja2 for email templates
- uvicorn for ASGI server
- pytest + httpx for testing
- python-dotenv for config

## Architecture
- Layered: api/v1/routes → services → repositories
- Dependency injection via FastAPI Depends
- Strategy pattern for AI providers
- Global error handler with custom exception hierarchy
- BackgroundTasks for non-blocking email dispatch

## Code Style
- Type hints everywhere (strict mypy mode)
- No comments unless business logic is non-trivial
- F-strings only (no .format() or %)
- Async for I/O-bound operations
- Pydantic models in schemas/ only
- Services never import from api/ layer
- Repositories never import from services/ layer

## Testing
- pytest with async fixtures
- Mock external services (AI, SMTP) in tests
- Fixtures in conftest.py per test directory
- Test file mirrors source path (tests/api/v1/routes/test_contact.py)

## Conventions
- Use `from app.core.config import settings` for all config
- Correlation ID via middleware, passed through Request
- JSON-structured logging to files (logs/ dir)
- Rate limiting: sliding window log algorithm
- Versioned API: /api/v1/*

## Files to never modify
- AGENTS.md
- .env.example
- .gitignore
- Makefile
- docker-compose.yml
- Dockerfile
- README.md (only by explicit user request)

## AI Integration
- AI module in app/ai/ with base Strategy class
- Fallback chain: OpenAI → rule-based classifier
- All prompts documented in README
- AI failures never crash the endpoint (graceful degradation)
