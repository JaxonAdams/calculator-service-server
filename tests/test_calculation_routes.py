import json
from unittest.mock import patch

import pytest

from app import app
from services.jwt_service import JWTService


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_header():
    token = JWTService().generate_token(user_id=1)
    return {"Authorization": f"Bearer {token}"}


def test_get_previous_calculations_is_protected(client):

    response = client.get("/api/v1/calculations")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Missing or invalid authorization header"}


@patch("routes.calculations.DBService")
def test_get_previous_calculations(mock_db_service, client, auth_header):

    mock_calculations = [
        {
            "id": 2,
            "operation": {
                "id": 3,
                "type": "multiplication",
                "cost": "0.25",
            },
            "user": {
                "id": 1,
                "username": "test.user@example.com",
                "status": "active",
            },
            "amount": 1,
            "calculation": json.dumps({"operation": "multiplication", "operands": [2, 2, 3], "result": 12}),
            "user_balance": "24.65",
            "date": "2024-11-02 12:45:00"
        },
        {
            "id": 1,
            "operation": {
                "id": 1,
                "type": "addition",
                "cost": "0.1",
            },
            "user": {
                "id": 1,
                "username": "test.user@example.com",
                "status": "active",
            },
            "amount": 1,
            "calculation": json.dumps({"operation": "addition", "operands": [21, 21], "result": 42}),
            "user_balance": "24.9",
            "date": "2024-11-02 12:42:00"
        },
    ]

    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = (
        mock_calculations
    )

    response = client.get("/api/v1/calculations", headers=auth_header)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"results": mock_calculations}


