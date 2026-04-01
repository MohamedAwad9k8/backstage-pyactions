import os

from fastapi.testclient import TestClient


def test_no_auth_when_token_not_set(client):
    """When API_TOKEN is not set, requests pass through without auth."""
    response = client.get("/health")
    assert response.status_code == 200


def test_auth_rejects_missing_token(monkeypatch):
    """When API_TOKEN is set, requests without token are rejected."""
    monkeypatch.setenv("API_TOKEN", "test-secret-token")

    # Re-import to pick up new settings
    from app.core.config import Settings
    import app.core.security as sec
    import app.core.config as cfg

    cfg.settings = Settings()
    sec.settings = cfg.settings

    from main import app
    test_client = TestClient(app)

    response = test_client.post(
        "/create-new-service",
        json={
            "ticket": "SRE-1234",
            "service-name": "test-svc",
            "service-path": "/backend",
        },
    )
    assert response.status_code == 403
