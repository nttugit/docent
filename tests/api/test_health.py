from fastapi.testclient import TestClient

from docent import __version__


def test_health_returns_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_reports_version_and_env(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body["version"] == __version__
    assert body["env"] == "test"


def test_unknown_route_returns_404(client: TestClient) -> None:
    assert client.get("/nope").status_code == 404
