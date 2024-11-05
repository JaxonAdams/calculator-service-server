from unittest.mock import patch

import pytest

from app import app
from config import USER_STARTING_BALANCE
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


def test_get_balance_is_protected(client):

    response = client.get("/api/v1/users/1/balance")

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data == {"error": "Missing or invalid authorization header"}


@patch("routes.user.DBService")
def test_get_balance(mock_db_service, client, auth_header):

    mock_db = mock_db_service.return_value.__enter__.return_value
    mock_db.fetch_records.return_value = [{"user_balance": "18.20"}]

    response = client.get(
        "/api/v1/users/1/balance",
        headers=auth_header,
    )

    assert response.status_code == 200
    assert response.get_json() == {"balance": "18.20"}


@patch("routes.user.DBService")
def test_get_balance_invalid_user(mock_db_service, client, auth_header):

    mock_db = mock_db_service.return_value.__enter__.return_value
    mock_db.fetch_records.side_effect = [None, None]

    response = client.get(
        "/api/v1/users/99/balance",
        headers=auth_header,
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "User with ID 99 not found"}


@patch("routes.user.DBService")
def test_get_balance_new_user(mock_db_service, client, auth_header):

    mock_db = mock_db_service.return_value.__enter__.return_value
    mock_db.fetch_records.side_effect = [None, {"id": "1"}]

    response = client.get(
        "/api/v1/users/1/balance",
        headers=auth_header,
    )

    assert response.status_code == 200
    assert response.get_json() == {"balance": USER_STARTING_BALANCE}
