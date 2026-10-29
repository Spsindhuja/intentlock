from fastapi.testclient import TestClient

from app.main import app


def test_root_redirects_to_api_docs() -> None:
    with TestClient(app) as client:
        response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_health_reports_process_liveness() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_reports_database_connectivity() -> None:
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dependencies": {"database": "ok"},
    }


def test_unknown_route_returns_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/not-a-real-route")

    assert response.status_code == 404
