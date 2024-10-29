from unittest.mock import patch

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("routes.auth.DBService")
@patch("routes.auth.checkpw")
@patch("routes.auth.jwt_service.generate_token")
def test_login_success(mock_generate_token, mock_checkpw, mock_db_service, client):

    # mock various functions which are called when a user is logged in
    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"id": 1, "username": "user", "password": "$2b$12$somethinghashed"}
    ]

    mock_checkpw.return_value = True

    mock_generate_token.return_value = "mocked_token"

    # perform a login request
    response = client.post(
        "/auth/login",
        json={"username": "user", "password": "password"},
    )

    # check the response returned
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"logged_in": True, "token": "mocked_token"}
    mock_checkpw.assert_called_once_with(b"password", b"$2b$12$somethinghashed")


@patch("routes.auth.DBService")
def test_login_invalid_user(mock_db_service, client):

    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = []

    response = client.post(
        "/auth/login",
        json={"username": "notauser", "password": "password"},
    )

    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data == {"error": "User 'notauser' not found"}


@patch("routes.auth.DBService")
@patch("routes.auth.checkpw")
def test_login_invalid_password(mock_checkpw, mock_db_service, client):

    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"id": 1, "username": "user", "password": "$2b$12$somethinghashed"}
    ]

    mock_checkpw.return_value = False

    response = client.post(
        "/auth/login", json={"username": "user", "password": "invalid_password"}
    )

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data == {"error": "Invalid password"}
    mock_checkpw.assert_called_once_with(b"invalid_password", b"$2b$12$somethinghashed")


@patch("routes.auth.DBService")
def test_login_missing_fields(mock_db_service, client):

    # missing both fields
    response = client.post(
        "/auth/login",
        json={},
    )
    assert response.status_code == 409
    assert response.get_json() == {"error": "Field 'username' is required."}

    # missing username
    response = client.post(
        "/auth/login",
        json={"password": "password"},
    )
    assert response.status_code == 409
    assert response.get_json() == {"error": "Field 'username' is required."}

    response = client.post(
        "/auth/login",
        json={"username": "user"},
    )
    assert response.status_code == 409
    assert response.get_json() == {"error": "Field 'password' is required."}
