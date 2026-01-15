

from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


# Helpers (simple, inline)
class FakePoint:
    def __init__(self, score, payload):
        self.score = score
        self.payload = payload


class FakeResults:
    def __init__(self, points):
        self.points = points


FAKE_VECTOR_RESULTS = FakeResults(points=[
    FakePoint(
        score=0.8,
        payload={
            "locality": "Andheri West",
            "price": 7500000,
            "bhk": 1,
            "area_sqft": 500,
            "amenities": ["Gymnasium"]
        }
    )
])


# Tests
@patch("api.query.explain_results", return_value="Nice explanation")
@patch("api.query.geo_vector_search", return_value=FAKE_VECTOR_RESULTS)
@patch("api.query.embed", return_value=[0.1] * 384)
@patch("api.query.geocode", return_value=(19.12, 72.88))
def test_basic_real_estate_query(
    mock_geo, mock_embed, mock_search, mock_explain
):
    response = client.post(
        "/api/ask",
        json={
            "query": "1 bhk flat in mumbai",
            "location": "Mumbai",
            "radius_km": 15,
            "bhk": 0,
            "max_price": 0,
            "require_gym": False
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["bhk"] == 1
    assert "explanation" in data


def test_irrelevant_query_rejected():
    response = client.post(
        "/api/ask",
        json={
            "query": "iron man is awesome",
            "location": "Mumbai",
            "radius_km": 15
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert "not appear to be related to real estate" in data["explanation"].lower()


def test_city_mismatch_rejected():
    response = client.post(
        "/api/ask",
        json={
            "query": "flat in pune",
            "location": "Mumbai",
            "radius_km": 15
        }
    )

    assert response.status_code == 200
    assert "searched for properties in pune" in response.json()["explanation"].lower()


