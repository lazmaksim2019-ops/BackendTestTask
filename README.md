# Backend Developer Landing API

Full-cycle backend service for a developer landing page with AI integration, email notifications, rate limiting, and structured logging.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.12 |
| **Framework** | FastAPI (async) |
| **Validation** | Pydantic v2 |
| **AI Provider** | Agnes AI (OpenAI-compatible) + rule-based fallback |
| **Templating** | Jinja2 (HTML emails) |
| **Storage** | JSON files (contacts) + SQLite (rate limits, stats) |
| **Testing** | pytest + httpx TestClient |
| **Infra** | Docker / docker-compose |

**Why FastAPI?** Native async support, automatic OpenAPI/Swagger docs via Pydantic, excellent performance, and built-in dependency injection — ideal for IO-bound workloads like AI calls and email dispatch.

---

## Architecture

```
app/
├── api/v1/routes/      # HTTP layer — only request parsing and response serialization
├── schemas/             # Pydantic models for validation and serialization
├── services/            # Business logic — orchestrates AI, email, and persistence
├── repositories/        # Data access — abstracts file and SQLite storage
├── ai/                  # AI strategies — Strategy pattern for provider switching
├── middleware/           # Cross-cutting concerns — logging, rate limiting, correlation IDs
├── core/                # Config, DI, exceptions, error handlers
└── templates/           # Jinja2 email templates
```

### Design Patterns

- **Layered Architecture**: Controllers → Services → Repositories (strict one-way dependency)
- **Strategy Pattern**: AI providers interchangeable via `AIStrategy` base class
- **Dependency Injection**: FastAPI `Depends()` for service wiring
- **Background Tasks**: Email dispatch via FastAPI `BackgroundTasks` (non-blocking)
- **Sliding Window Log**: Rate limiting algorithm (not a simple counter)

---

## API Endpoints

### `POST /api/v1/contact`
Submit a contact form with AI-powered analysis.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "comment": "Great portfolio! I'd like to discuss a project."
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Your message has been received...",
  "correlation_id": "uuid",
  "ai_analysis": {
    "sentiment": "positive",
    "sentiment_score": 0.7,
    "request_type": "collaboration",
    "suggested_reply": "Dear John,..."
  }
}
```

**Error responses:**
| Status | Meaning |
|---|---|
| 400 | Validation error (missing/invalid fields) |
| 429 | Rate limit exceeded |
| 502 | External service unavailable (AI or email) |

### `GET /api/v1/health`
```json
{ "status": "healthy", "version": "1.0.0" }
```

### `GET /api/v1/metrics`
```json
{ "stats": { "total_contacts": 42, "type_collaboration": 10 } }
```

### Interactive Docs
- Swagger: `/api/docs`
- ReDoc: `/api/redoc`

---

## AI Integration

### Pipeline (3-in-1 analysis)

1. **Sentiment Analysis** — classifies tone as positive/neutral/negative
2. **Request Classification** — categorizes as technical_question / collaboration / bug_report / feature_request / general
3. **Reply Generation** — produces a professional contextual response

### Provider Chain

```
Agnes AI (OpenAI-compatible API)
    └─ on failure → Rule-based classifier (keyword matching + templates)
```

The fallback is transparent: if the primary AI provider is unavailable or returns invalid JSON, the service degrades gracefully to a deterministic rule-based engine. The endpoint **never crashes** due to AI failure.

### Prompts Used

**System prompt for Agnes AI:**
```
You are a contact form analysis assistant. Analyze the user's message
and return ONLY valid JSON with these fields:
- sentiment: one of "positive", "neutral", "negative"
- sentiment_score: float from 0.0 to 1.0
- request_type: one of "technical_question", "collaboration",
  "bug_report", "feature_request", "general"
- suggested_reply: a brief professional reply addressing the query

Return ONLY the JSON object, no markdown, no code blocks.
```

### What was AI-generated

- The entire `app/ai/agnes.py` strategy — prompt engineering and API integration
- Email HTML templates — Jinja2 structure
- Frontend `static/index.html` — form UI with JS validation
- Test stubs for the rule-based classifier
- 90% of the README (this file)
- The rule-based fallback's keyword lists and reply templates

**Manually adjusted:**
- Architecture decisions (layering, DI wiring)
- Strategy Pattern interface (`AIStrategy` base class)
- Error handling hierarchy and global handler
- Rate limiter algorithm (sliding window log)
- Middleware ordering and correlation ID propagation
- All business logic in `ContactService`

---

## Storage

| Data | Storage | Location |
|---|---|---|
| Contact submissions | JSON file | `data/contacts.json` |
| Rate limit records | JSON file | `data/rate_limit_log.json` |
| Statistics | JSON file | `data/stats.json` |
| Request logs | Text file | `logs/app.log` |

All storage is file-based per the requirements. Architecture is abstracted via `Repository` classes, making migration to a database a single implementation change.

---

## Getting Started

### Prerequisites

- Python 3.12+
- (Optional) Docker + docker-compose

### Local Development

```bash
# 1. Clone and enter directory
git clone https://github.com/lazmaksim2019-ops/BackendTestTask.git
cd BackendTestTask

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — at minimum set AI_API_KEY for AI features

# 5. Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker compose up -d
# App available at http://localhost:8000
```

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `AI_API_KEY` | No | — | Agnes AI API key. Falls back to rule-based if empty |
| `AI_API_BASE_URL` | No | `https://apihub.agnes-ai.com/v1` | API endpoint |
| `AI_MODEL` | No | `agnes-2.0-flash` | Model name |
| `SMTP_HOST` | No | — | SMTP server. Emails logged to file if empty |
| `SMTP_PORT` | No | `587` | SMTP port |
| `SMTP_USER` | No | — | SMTP username |
| `SMTP_PASS` | No | — | SMTP password |
| `APP_OWNER_EMAIL` | No | `owner@example.com` | Notification recipient |
| `RATE_LIMIT_REQUESTS` | No | `10` | Max POST requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | No | `60` | Rate limit window |

### Testing

```bash
pytest -v
```

### Makefile

```bash
make dev      # Run dev server with auto-reload
make test     # Run tests
make clean    # Clean cache files
make docker-up   # Start via docker-compose
```

---

## Example Requests (curl)

```bash
# Submit contact
curl -X POST http://localhost:8000/api/v1/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "comment": "Great work! Would love to collaborate."
  }'

# Health check
curl http://localhost:8000/api/v1/health

# Metrics
curl http://localhost:8000/api/v1/metrics
```

---

## Deployment

The app is Docker-ready. Deploy to Railway / Render / AnyHost:

```bash
# Build and push
docker build -t backend-landing .
docker tag backend-landing registry.railway.app/your-project/backend-landing
docker push ...

# Or use Render's Blueprint with docker-compose.yml
```
