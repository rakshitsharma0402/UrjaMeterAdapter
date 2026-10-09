
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.services.urja_client import UrjaAuthenticationError


class FakeUrjaClient:
    async def search_meters(self, q="", page=1):

        if q == "AUTH_FAIL":
            raise UrjaAuthenticationError("Authentication failed.")

        if q == "INVALID_METER":
            return {
                "data": [],
                "total": 0,
                "page": page,
                "pageSize": 20,
            }

        return {
            "data": [
                {
                    "meterId": "J100019",
                    "serialNo": "GE24621",
                    "make": "L&T",
                    "phaseType": "single",
                    "installStatus": "Decommissioned",
                    "dtCode": "DT-020",
                }
            ],
            "total": 1,
            "page": page,
            "pageSize": 20,
        }

    async def get_energy(self, meter_id):
        return {"data": []}

    async def get_geo(self, meter_id):
        return {
            "data": {
                "latitude": "27.01089",
                "longitude": "75.83053",
            }
        }

    async def close(self):
        pass



@pytest.fixture
def client():
    with TestClient(app) as test_client:
        # Set the fake after startup, because lifespan creates a real client.
        app.state.urja_client = FakeUrjaClient()
        yield test_client

def test_search_meters_success(client):
    response = client.get(
        "/api/v1/meters",
        params={"q": "J100019", "page": 1},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["total"] == 1
    assert body["data"][0]["meter_id"] == "J100019"
    assert body["data"][0]["serial_no"] == "GE24621"


def test_search_meters_empty_result(client):
    response = client.get(
        "/api/v1/meters",
        params={"q": "INVALID_METER", "page": 1},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["data"] == []
    assert body["total"] == 0


def test_authentication_failure_returns_502(client):
    response = client.get(
        "/api/v1/meters",
        params={"q": "AUTH_FAIL", "page": 1},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Upstream authentication failed."
    }


def test_page_zero_returns_422(client):
    response = client.get(
        "/api/v1/meters",
        params={"q": "J100019", "page": 0},
    )

    assert response.status_code == 422

