from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_ingest_endpoint():
    response = client.post("/api/ingest")
    assert response.status_code == 200
    assert response.json()["message"] == "Use script for ingestion"
