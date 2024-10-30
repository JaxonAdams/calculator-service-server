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


def test_get_operations_no_auth(client):

    response = client.get("/api/v1/operations")

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data == {"error": "Missing or invalid authorization header"}


def test_get_operations_invalid_auth(client):

    invalid_auth = {"Authorization": "Bearer not-a-jwt"}
    response = client.get("/api/v1/operations", headers=invalid_auth)

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data == {"error": "Invalid token"}

    expired_token = JWTService(expiration_hours=-1).generate_token(user_id=1)
    expired_auth = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/operations", headers=expired_auth)

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data == {"error": "Token has expired"}


@patch("routes.operation.DBService")
def test_get_operations(mock_db_service, client, auth_header):

    mock_operations = [
        {"id": 1, "type": "addition", "cost": 0.1},
        {"id": 2, "type": "subtraction", "cost": 0.1},
        {"id": 3, "type": "multiplication", "cost": 0.25},
        {"id": 4, "type": "division", "cost": 0.25},
        {"id": 5, "type": "square_root", "cost": 0.75},
        {"id": 6, "type": "random_string", "cost": 1.0},
    ]

    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = (
        mock_operations
    )

    response = client.get("/api/v1/operations", headers=auth_header)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"results": mock_operations}
