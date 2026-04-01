def test_modules_registered(client):
    """All modules from modules.yaml should be registered as routes."""
    routes = [r.path for r in client.app.routes]
    assert "/create-new-service" in routes
    assert "/deploy-existing-service-to-prod" in routes
    assert "/whitelist-domain" in routes


def test_create_service_returns_validation_error(client):
    """Calling a module endpoint with missing required fields returns 422."""
    response = client.post("/create-new-service", json={})
    assert response.status_code == 422


def test_create_service_accepts_valid_payload(client):
    """Calling a module endpoint with valid params returns 200."""
    response = client.post(
        "/create-new-service",
        json={
            "ticket": "SRE-1234",
            "service-name": "test-service",
            "service-path": "/backend/services",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["service_name"] == "test-service"
