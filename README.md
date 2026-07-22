# Backend Developer Landing API

![CI](https://github.com/lazmaksim2019-ops/BackendTestTask/actions/workflows/ci.yml/badge.svg?branch=master)

Backend-сервис для лендинг-презентации разработчика с AI-интеграцией, email-уведомлениями, rate limiting и структурированным логированием.

Живое демо: [https://backendtesttask-3px9.onrender.com]

---

## Стек технологий

| Слой | Технология |
|---|---|
| **Язык** | Python 3.12 |
| **Фреймворк** | FastAPI (async) |
| **Валидация** | Pydantic v2 |
| **AI-провайдер** | Agnes AI (OpenAI-совместимый) + rule-based fallback |
| **Шаблонизатор** | Jinja2 (HTML-письма) |
| **Хранение** | SQLite (контакты, статистика) + JSON-файлы (rate limit) |
| **Тестирование** | pytest + httpx TestClient |
| **Инфраструктура** | Docker / docker-compose |

**Почему FastAPI?** Нативная асинхронность, автоматическая OpenAPI/Swagger документация через Pydantic, встроенный механизм Dependency Injection — идеально для IO-bound нагрузок (AI-запросы, отправка писем).

---

## Архитектура

```
app/
├── api/v1/routes/       # HTTP-слой — только парсинг запроса и сериализация ответа
├── schemas/              # Pydantic-модели для валидации и сериализации
├── services/             # Бизнес-логика — оркестрация AI, email, сохранения
├── repositories/         # Доступ к данным — абстракция над JSON-файлами
├── ai/                   # AI-стратегии — паттерн Strategy для смены провайдеров
├── middleware/            # Сквозные задачи — логирование, rate limit, correlation ID
├── core/                 # Конфиг, DI, исключения, обработчик ошибок
└── templates/            # Jinja2-шаблоны писем
```

### Паттерны проектирования

- **Слоистая архитектура**: Routes → Services → Repositories (строгая однонаправленная зависимость)
- **Strategy Pattern**: Провайдеры AI взаимозаменяемы через базовый класс `AIStrategy`
- **Dependency Injection**: Провязка сервисов через FastAPI `Depends()`
- **Synchronous Email**: Отправка писем до возврата ответа — полный цикл: запрос → валидация → AI → email → ответ
- **Sliding Window Log**: Алгоритм rate limiting (честное скользящее окно, а не простой счётчик)

---

## API Endpoints

### `POST /api/contact`
Отправка формы обратной связи с AI-анализом.

**Запрос:**
```json
{
  "name": "Иван Петров",
  "email": "ivan@example.com",
  "phone": "+71234567890",
  "comment": "Отличное портфолио! Хочу обсудить сотрудничество."
}
```

**Успешный ответ (201):**
```json
{
  "success": true,
  "message": "Ваше сообщение получено. Мы свяжемся с вами в ближайшее время.",
  "correlation_id": "uuid",
  "ai_analysis": {
    "sentiment": "positive",
    "sentiment_score": 0.7,
    "request_type": "collaboration",
    "suggested_reply": "Dear Иван Петров,..."
  }
}
```

AI-ошибки не возвращают `502` — сервис плавно деградирует до rule-based fallback, а затем до безопасной заглушки.

**Коды ошибок:**
| Статус | Описание |
|---|---|
| 422 | Ошибка валидации (некорректные поля) |
| 429 | Превышен лимит запросов (rate limit) |
| 502 | Email-сервис недоступен (только при настроенном SMTP) |

### `GET /api/health`
```json
{ "status": "healthy", "version": "1.0.0" }
```

### `GET /api/metrics`
```json
{ "stats": { "total_contacts": 42, "type_collaboration": 10 } }
```

### Версионированные эндпоинты
Все эндпоинты также доступны с префиксом `/api/v1/`:
- `POST /api/v1/contact`
- `GET /api/v1/health`
- `GET /api/v1/metrics`

### Интерактивная документация
- Swagger: `/api/docs`
- ReDoc: `/api/redoc`

---

## AI-интеграция

### Конвейер анализа (3 шага в одном запросе)

1. **Анализ тональности** — определение тона сообщения (позитив/нейтрал/негатив)
2. **Классификация типа запроса** — технический вопрос / коллаборация / баг / предложение / общее
3. **Генерация ответа** — профессиональный контекстный ответ

### Цепочка провайдеров

```
Agnes AI (OpenAI-совместимый API)
    └─ при ошибке → Rule-based классификатор (ключевые слова + шаблоны)
        └─ при ошибке → жёсткая заглушка (neutral/general)
```

Fallback прозрачен: если основной AI-провайдер недоступен или возвращает невалидный JSON, сервис плавно деградирует до детерминированного rule-based движка. Даже если rule-based упадёт — вернётся безопасная заглушка. Эндпоинт **никогда не падает** из-за ошибки AI.

### Используемые промпты

**System prompt для Agnes AI:**
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

---

## Валидация и обработка ошибок

### Валидация входных данных

Поля проходят многоуровневую проверку:

| Поле | Правила валидации |
|---|---|
| `name` | 2–100 символов, обрезка пробелов |
| `email` | Проверка формата через Pydantic `EmailStr` |
| `phone` | 10–20 символов, разрешены `+`, цифры, пробелы, тире, скобки; минимум 10 цифр |
| `comment` | 10–2000 символов, обрезка пробелов |

### Иерархия ошибок

```
AppError (базовый)
├── ValidationError (422)
├── NotFoundError (404)
├── RateLimitError (429)
├── AIError (502)
└── EmailError (502)
```

Глобальный обработчик перехватывает все исключения:
- Кастомные `AppError` → соответствующий HTTP-статус с детальным сообщением
- Необработанные исключения → 500 + логирование полного stack trace

### Rate Limiting

Алгоритм: **Sliding Window Log** — честное скользящее окно, которое не сбрасывается каждые N секунд, а непрерывно учитывает запросы внутри временного окна.

- По умолчанию: 10 POST-запросов за 60 секунд
- Ключ: IP-адрес клиента
- Хранение: JSON-файл
- При превышении возвращается `429 Too Many Requests` с заголовком `Retry-After`

---

## Хранение данных

| Данные | Хранилище | Путь |
|---|---|---|
| Обращения | SQLite | `data/app.db` (таблица `contacts`) |
| Статистика | SQLite | `data/app.db` (таблица `stats`) |
| Rate limit записи | JSON-файл | `data/rate_limit_log.json` |
| Логи запросов | Текстовый файл | `logs/app.log` |

**Почему SQLite?** Нулевая конфигурация, не требует отдельного сервера, идеально для демо-проекта. Таблицы создаются автоматически при старте приложения. Схема включает две таблицы: `contacts` (id, name, email, phone, comment, correlation_id, created_at) и `stats` (key, value) с `UPSERT`-логикой через `ON CONFLICT DO UPDATE`. Все хранилища абстрагированы через `Repository`-классы — замена на PostgreSQL требует только реализации другого репозитория без изменения сервисного слоя.

---

## Запуск проекта

### Локально

```bash
# Клонировать
git clone https://github.com/lazmaksim2019-ops/BackendTestTask.git
cd BackendTestTask

# Виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Зависимости
pip install -r requirements.txt

# Настройка .env
cp .env.example .env
# Обязательно укажите AI_API_KEY для работы AI-функций
# Agnes AI (бесплатно): https://agnes-ai.com

# Запуск
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker compose up -d
# Приложение доступно на http://localhost:8000
```

### Переменные окружения

| Переменная | Обязательная | По умолчанию | Описание |
|---|---|---|---|
| `AI_API_KEY` | Нет | — | API-ключ Agnes AI. Если пусто — rule-based fallback |
| `AI_API_BASE_URL` | Нет | `https://apihub.agnes-ai.com/v1` | URL API |
| `AI_MODEL` | Нет | `agnes-2.0-flash` | Название модели |
| `SMTP_HOST` | Нет | — | SMTP-сервер. Если пусто — письма пишутся в лог |
| `SMTP_PORT` | Нет | `587` | Порт SMTP |
| `SMTP_USER` | Нет | — | Пользователь SMTP |
| `SMTP_PASS` | Нет | — | Пароль SMTP |
| `APP_OWNER_EMAIL` | Нет | `owner@example.com` | Email владельца для уведомлений |
| `CORS_ORIGINS` | Нет | `http://localhost:3000,...` | Разрешённые CORS-источники |
| `RATE_LIMIT_REQUESTS` | Нет | `10` | Макс. POST-запросов за окно |
| `RATE_LIMIT_WINDOW_SECONDS` | Нет | `60` | Окно rate limit |

### Тестирование

```bash
pytest -v                # без покрытия
pytest --cov=app -v      # с отчётом о покрытии
```

### Makefile

```bash
make dev      # Запуск dev-сервера с авто-перезагрузкой
make test     # Запуск тестов
make cov      # Тесты с отчётом о покрытии
make clean    # Очистка кеша
make docker-up   # Запуск через docker-compose
```

---

## Примеры запросов (curl)

```bash
# Отправить обращение
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван Петров",
    "email": "ivan@example.com",
    "phone": "+71234567890",
    "comment": "Отличная работа! Хочу предложить сотрудничество."
  }'

# Проверка здоровья
curl http://localhost:8000/api/health

# Статистика
curl http://localhost:8000/api/metrics
```

---

## Email-уведомления

- **Шаблоны**: Jinja2 с автоэкранированием HTML
- **Отправка**: Синхронно в рамках запроса — email отправляется до возврата ответа клиенту
- **Два письма**: владельцу сайта + копия пользователю
- **SMTP**: через `aiosmtplib` с STARTTLS
- **Fallback**: если SMTP не настроен — письмо логируется в файл (без PII)

---

## Что сделано с помощью AI

**Сгенерировано AI:**
- `app/ai/agnes.py` — интеграция с Agnes AI, промпт-инжиниринг
- Email-шаблоны (HTML)
- Фронтенд `static/index.html` — форма с JS-валидацией
- Тесты rule-based классификатора
- Большая часть README
- Keyword-списки и шаблоны ответов для rule-based fallback

**Написано вручную:**
- Архитектурные решения (слои, DI, связи между модулями)
- Интерфейс `AIStrategy` и паттерн Strategy
- Иерархия исключений и глобальный error handler
- Алгоритм Sliding Window Log для rate limiter
- Порядок middleware и propagation correlation ID
- Бизнес-логика `ContactService`
- Все правки после код-ревью (эта версия)

---

## Деплой

Приложение готово к деплою на Render / Railway / AnyHost:

```bash
# 1. Запушить в GitHub
git push origin master

# 2. На Render: New + Web Service
#    - Repository: https://github.com/lazmaksim2019-ops/BackendTestTask
#    - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
#    - Добавить переменные окружения из .env.example

# 3. Или через Docker:
docker build -t backend-landing .
docker push ...
```

---

## Ограничения (Known limitations)

- **File-based rate limiter** подходит для single-worker/demo-режима. Для production рекомендуется Redis или БД.
- **File storage** не рассчитан на высокую конкурентность. При нескольких одновременных запросах возможны race conditions при записи в JSON-файлы. В production — замена на PostgreSQL/Redis.
- **Email** отправляется синхронно для демонстрации полного цикла. В production отправку следует выносить в очередь (Celery / RabbitMQ / Redis Queue).
- **Статистика** в JSON-файле не оптимизирована для высоких нагрузок. Для production — агрегация в БД с кешированием.

---

## Лицензия

MIT

## Автор

**Александр Лазаренко** — Fullstack Developer (React + FastAPI + AI)

[![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/lazalex81)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lazmaksim2019-ops)
