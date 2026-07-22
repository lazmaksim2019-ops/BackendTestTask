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
        assert data["ai_analysis"] is None

    def test_submit_contact_validation_error(self, client):
        response = client.post("/api/v1/contact", json={"name": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_contact_missing_field(self, client):
        response = client.post(
            "/api/v1/contact",
            json={"name": "Test", "email": "invalid"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_health_endpoint(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    def test_metrics_endpoint(self, client):
        response = client.get("/api/v1/metrics")
        assert response.status_code == status.HTTP_200_OK
        assert "stats" in response.json()
