import pytest
from fastapi import status

CONTACT_PAYLOAD = {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "comment": "Great portfolio! I'd like to discuss a collaboration opportunity.",
}


class TestContactEndpoint:
    def test_submit_contact_success(self, client):
        response = client.post("/api/v1/contact", json=CONTACT_PAYLOAD)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["correlation_id"] is not None
        assert data["ai_analysis"] is not None
        assert data["ai_analysis"]["sentiment"] in ("positive", "neutral", "negative")

    def test_submit_contact_validation_error(self, client):
        response = client.post("/api/v1/contact", json={"name": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_submit_contact_missing_field(self, client):
        response = client.post(
            "/api/v1/contact",
            json={"name": "Test", "email": "invalid"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_health_endpoint(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    def test_metrics_endpoint(self, client):
        response = client.get("/api/v1/metrics")
        assert response.status_code == status.HTTP_200_OK
        assert "stats" in response.json()

    def test_rate_limit_exceeded(self, client, monkeypatch):
        from pathlib import Path
        from app.core.config import settings

        monkeypatch.setattr(settings, "rate_limit_requests", 2)
        monkeypatch.setattr(settings, "rate_limit_window_seconds", 60)

        log_file = Path(settings.data_dir) / "rate_limit_log.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text("[]", encoding="utf-8")

        for _ in range(settings.rate_limit_requests):
            resp = client.post("/api/v1/contact", json=CONTACT_PAYLOAD)
            assert resp.status_code == status.HTTP_201_CREATED

        resp = client.post("/api/v1/contact", json=CONTACT_PAYLOAD)
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers

        log_file.write_text("[]", encoding="utf-8")
