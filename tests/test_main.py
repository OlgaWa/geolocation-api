import os
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from app.database import get_db
from app.main import app


@pytest_asyncio.fixture
async def test_db():
    client = AsyncMongoMockClient()
    db = client["test_db"]
    yield db
    client.close()


@pytest_asyncio.fixture
async def client(test_db):
    # Override the dependency before creating the client
    app.dependency_overrides[get_db] = lambda: test_db

    transport = ASGITransport(app=app)
    with patch.dict(os.environ, {"IPSTACK_API_KEY": "provide_api_key"}):
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client

    # Clean up the override after the test
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_geolocation_ok(client, test_db):
    request_data = {"geo_identifier": "example.com"}
    response = await client.post("/geolocations", json=request_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["ip"] is not None
    assert response_data["country"] is not None


@pytest.mark.asyncio
async def test_create_geolocation_409(client, test_db):
    request_data = {"geo_identifier": "example.com"}
    await client.post("/geolocations", json=request_data)

    # Using the same request payload again
    response = await client.post("/geolocations", json=request_data)
    assert response.status_code == 409
    assert "already exists in the database." in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_geolocation_422(client):
    response = await client.post(
        "/geolocations", json={"geo_identifier": "abc"}
    )
    assert response.status_code == 422
    assert "Could not resolve URL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_geolocation_ok(client, test_db):
    # Insert a document to the mock DB
    await test_db["geolocations"].insert_one(
        {
            "ip": "93.184.216.34",
            "ip_type": "ipv4",
            "city": "Lombard",
            "country": "United States",
            "region": "",
            "latitude": 41.877628326416016,
            "longitude": -88.0197982788086,
        }
    )

    response = await client.get("/geolocations/93.184.216.34")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["ip"] == "93.184.216.34"
    assert response_data["country"] == "United States"


@pytest.mark.asyncio
async def test_get_geolocation_404(client, test_db):
    # Trying to get a document from an empty db
    response = await client.get("/geolocations/192.168.1.1")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_geolocation_422(client):
    response = await client.get("/geolocations/abc")
    assert response.status_code == 422
    assert "Could not resolve URL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_geolocation_ok(client, test_db):
    # Insert a document to the mock DB
    await test_db["geolocations"].insert_one(
        {
            "ip": "93.184.216.34",
            "ip_type": "ipv4",
            "city": "Lombard",
            "country": "United States",
            "region": "",
            "latitude": 41.877628326416016,
            "longitude": -88.0197982788086,
        }
    )

    response = await client.delete("/geolocations/93.184.216.34")
    assert response.status_code == 204

    # Ensure the document is deleted
    document = await test_db["geolocations"].find_one({"ip": "93.184.216.34"})
    assert document is None


@pytest.mark.asyncio
async def test_delete_geolocation_422(client, test_db):
    # Should not throw an error for the endpoint to be idempotent
    response = await client.delete("/geolocations/abc")
    assert response.status_code == 422
    assert "Could not resolve URL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_geolocations_ok(client, test_db):
    # Insert multiple documents to the mock DB
    await test_db["geolocations"].insert_many(
        [
            {
                "ip": "93.184.216.34",
                "ip_type": "ipv4",
                "city": "Lombard",
                "country": "United States",
                "region": "",
                "latitude": 41.877628326416016,
                "longitude": -88.0197982788086,
            },
            {
                "ip": "192.0.2.1",
                "ip_type": "ipv4",
                "country": "Test Country",
                "city": "Test City",
                "region": "",
                "latitude": 21.877628326416016,
                "longitude": -68.0197982788086,
            },
        ]
    )

    response = await client.get("/geolocations")
    assert response.status_code == 200
    response_data = response.json()["geolocations"]
    assert len(response_data) == 2
    assert response_data[0]["ip"] == "93.184.216.34"
    assert response_data[1]["ip"] == "192.0.2.1"
