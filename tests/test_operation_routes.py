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


@patch("routes.operation.DBService")
def test_get_op_by_id(mock_db_service, client, auth_header):

    mock_operation = {"id": 5, "type": "square_root", "cost": 0.75}

    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        mock_operation
    ]

    response = client.get("/api/v1/operations/5", headers=auth_header)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == mock_operation


@patch("routes.operation.DBService")
def test_get_op_by_id_not_found(mock_db_service, client, auth_header):

    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = []

    response = client.get("/api/v1/operations/999", headers=auth_header)

    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data == {"error": "Operation with ID 999 not found"}


def test_get_op_by_id_is_protected(client):

    response = client.get("/api/v1/operations/1")
    assert response.status_code == 401


@patch("routes.operation.DBService")
def test_create_operation(mock_db_service, client, auth_header):

    mock_db_service.return_value.__enter__.return_value.insert_record.return_value = 1

    item_data = {"type": "modulo", "cost": 0.35}

    response = client.post(
        "/api/v1/operations",
        json=item_data,
        headers=auth_header,
    )

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data == item_data | {"id": 1}

    mock_db_service.return_value.__enter__.return_value.insert_record.assert_called_once_with(
        "operation", item_data
    )


@patch("routes.operation.DBService")
def test_create_op_missing_fields(mock_db_service, client, auth_header):

    item_data = {"cost": 0.35}
    response = client.post(
        "/api/v1/operations",
        json=item_data,
        headers=auth_header,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'type' is required"}

    item_data = {"type": "modulo"}
    response = client.post(
        "/api/v1/operations",
        json=item_data,
        headers=auth_header,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'cost' is required"}

    item_data = {}
    response = client.post(
        "/api/v1/operations",
        json=item_data,
        headers=auth_header,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'type' is required"}


def test_create_op_is_protected(client):

    item_data = {"type": "modulo", "cost": 0.35}

    response = client.post(
        "/api/v1/operations",
        json=item_data,
    )

    assert response.status_code == 401
