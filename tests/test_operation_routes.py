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


@pytest.fixture
def admin_auth_header():

    token = JWTService().generate_admin_token(
        "UNIT TEST SUITE",
        "FAKE TOKEN FOR UNIT TESTING",
    )

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

    mock_db_service.return_value.__enter__.return_value.count_records.return_value = 6

    mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = (
        mock_operations
    )

    expected_results = [
        {
            "id": 1,
            "type": "addition",
            "cost": 0.1,
            "options": {
                "operand_type": "number",
                "operand_count": "variable",
                "description": "Add any number of operands together.",
            }
        },
        {
            "id": 2,
            "type": "subtraction",
            "cost": 0.1,
            "options": {
                "operand_type": "number",
                "operand_count": "variable",
                "description": "Subtract any number of operands from the first operand.",
            }
        },
        {
            "id": 3,
            "type": "multiplication",
            "cost": 0.25,
            "options": {
                "operand_type": "number",
                "operand_count": "variable",
                "description": "Multiply any number of operands together.",
            }
        },
        {
            "id": 4,
            "type": "division",
            "cost": 0.25,
            "options": {
                "operand_type": "number",
                "operand_count": "variable",
                "description": "Divide the first operand by all subsequent operands.",
            }
        },
        {
            "id": 5,
            "type": "square_root",
            "cost": 0.75,
            "options": {
                "operand_type": "number",
                "operand_count": 1,
                "description": "Calculate the square root of the operand.",
            }
        },
        {
            "id": 6,
            "type": "random_string",
            "cost": 1.0,
            "options": {
                "operand_type": "dictionary",
                "operand_count": 1,
                "description": "Generate a random string based on the provided options.",
                "options": {
                    "string_length": {
                        "type": "int",
                        "description": "The length of the random string to generate.",
                    },
                    "include_digits": {
                        "type": "bool",
                        "description": "Include digits (0-9) in the random string.",
                    },
                    "include_uppercase_letters": {
                        "type": "bool",
                        "description": "Include uppercase letters (A-Z) in the random string.",
                    },
                    "include_lowercase_letters": {
                        "type": "bool",
                        "description": "Include lowercase letters (a-z) in the random string.",
                    },
                },
            }
        },
    ]

    expected_metadata = {
        "total": 6,
        "page": 1,
        "page_size": 10,
    }

    response = client.get("/api/v1/operations", headers=auth_header)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"results": expected_results, "metadata": expected_metadata}


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
@patch("services.jwt_service.DBService")
def test_create_operation(
    jwt_mock_db_service,
    routes_mock_db_service,
    client,
    admin_auth_header,
):

    jwt_mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"api_key": "valid_api_key"}
    ]

    routes_mock_db_service.return_value.__enter__.return_value.insert_record.return_value = (
        1
    )

    operation_data = {"type": "modulo", "cost": 0.35}

    response = client.post(
        "/api/v1/operations",
        json=operation_data,
        headers=admin_auth_header,
    )

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data == operation_data | {"id": 1}

    routes_mock_db_service.return_value.__enter__.return_value.insert_record.assert_called_once_with(
        "operation", operation_data
    )


@patch("services.jwt_service.DBService")
def test_create_op_missing_fields(jwt_mock_db_service, client, admin_auth_header):

    jwt_mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"api_key": "valid_api_key"}
    ]

    operation_data = {"cost": 0.35}
    response = client.post(
        "/api/v1/operations",
        json=operation_data,
        headers=admin_auth_header,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'type' is required"}

    operation_data = {"type": "modulo"}
    response = client.post(
        "/api/v1/operations",
        json=operation_data,
        headers=admin_auth_header,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'cost' is required"}

    operation_data = {}
    response = client.post(
        "/api/v1/operations",
        json=operation_data,
        headers=admin_auth_header,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'type' is required"}


def test_create_op_is_protected(client):

    operation_data = {"type": "modulo", "cost": 0.35}

    response = client.post(
        "/api/v1/operations",
        json=operation_data,
    )

    assert response.status_code == 401


@patch("routes.operation.DBService")
@patch("services.jwt_service.DBService")
def test_update_operation(
    jwt_mock_db_service,
    routes_mock_db_service,
    client,
    admin_auth_header,
):

    jwt_mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"api_key": "valid_api_key"}
    ]

    routes_mock_db_service.return_value.__enter__.return_value.update_record.return_value = (
        1
    )
    routes_mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"id": 3, "type": "multiplication", "cost": 0.99},
    ]

    operation_data = {"cost": 0.99}

    response = client.put(
        "/api/v1/operations/3",
        json=operation_data,
        headers=admin_auth_header,
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"id": 3, "type": "multiplication", "cost": 0.99}


def test_update_op_is_protected(client):

    operation_data = {"cost": 0.99}

    response = client.put(
        "/api/v1/operations/3",
        json=operation_data,
    )

    assert response.status_code == 401


@patch("services.jwt_service.DBService")
def test_update_op_no_fields_provided(jwt_mock_db_service, client, admin_auth_header):

    jwt_mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"api_key": "valid_api_key"}
    ]

    operation_data = {}

    response = client.put(
        "/api/v1/operations/3",
        json=operation_data,
        headers=admin_auth_header,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "You must specify a field to update."}


@patch("routes.operation.DBService")
@patch("services.jwt_service.DBService")
def test_delete_op(
    jwt_mock_db_service,
    routes_mock_db_service,
    client,
    admin_auth_header,
):

    jwt_mock_db_service.return_value.__enter__.return_value.fetch_records.return_value = [
        {"api_key": "valid_api_key"}
    ]

    mock_db = routes_mock_db_service.return_value.__enter__.return_value

    mock_db.fetch_records.side_effect = [
        [{"id": 3, "type": "multiplication", "cost": 0.1, "deleted": 0}],
        [{"id": 3, "type": "multiplication", "cost": 0.1, "deleted": 1}],
    ]

    mock_db.update_record.return_value = 1

    response = client.delete(
        "/api/v1/operations/3",
        headers=admin_auth_header,
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "Operation with ID 3 was deleted."}
