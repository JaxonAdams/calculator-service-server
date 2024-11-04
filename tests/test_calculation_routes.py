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


@patch("routes.calculation.DBService")
def test_get_previous_calculations(mock_db_service, client, auth_header):

    mock_calculations = [
        {
            "id": 2,
            "operation_id": 3,
            "operation_type": "multiplication",
            "operation_cost": "0.25",
            "user_id": 1,
            "username": "test.user@example.com",
            "user_status": "active",
            "calculation": json.dumps(
                {"operation": "multiplication", "operands": [2, 2, 3], "result": 12}
            ),
            "user_balance": "24.65",
            "date": "2024-11-02 12:45:00",
        },
        {
            "id": 1,
            "operation_id": 1,
            "operation_type": "addition",
            "operation_cost": "0.1",
            "user_id": 1,
            "username": "test.user@example.com",
            "user_status": "active",
            "calculation": json.dumps(
                {"operation": "addition", "operands": [21, 21], "result": 42}
            ),
            "user_balance": "24.9",
            "date": "2024-11-02 12:42:00",
        },
    ]

    formatted_results = [
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
            "calculation": {
                "operation": "multiplication",
                "operands": [2, 2, 3],
                "result": 12,
            },
            "user_balance": "24.65",
            "date": "2024-11-02 12:45:00",
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
            "calculation": {
                "operation": "addition",
                "operands": [21, 21],
                "result": 42,
            },
            "user_balance": "24.9",
            "date": "2024-11-02 12:42:00",
        },
    ]

    mock_db_service.return_value.__enter__.return_value.execute_query.return_value = (
        mock_calculations
    )

    response = client.get("/api/v1/calculations", headers=auth_header)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"results": formatted_results}


def test_run_calculation_is_protected(client):

    calculation_request = {
        "operation": "addition",
        "operands": [1, 3, 2],
    }

    response = client.post(
        "/api/v1/calculations/new",
        json=calculation_request,
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Missing or invalid authorization header"}


@patch("routes.calculation.DBService")
def test_run_calculation(mock_db_service, client, auth_header):

    mock_db = mock_db_service.return_value.__enter__.return_value

    mock_db.insert_record.return_value = 1  # new record ID
    mock_db.execute_query.return_value = [
        {"balance": "18.35"},
    ]
    mock_db.fetch_records.return_value = [{"id": 1, "type": "addition", "cost": "0.1"}]

    calculation_request = {
        "operation": "addition",
        "operands": [1, 3, 2],
    }

    response = client.post(
        "/api/v1/calculations/new",
        json=calculation_request,
        headers=auth_header,
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"operation": "addition", "operands": [1, 3, 2], "result": 6}


@patch("routes.calculation.DBService")
def test_run_calc_insufficient_funds(mock_db_service, client, auth_header):

    mock_db = mock_db_service.return_value.__enter__.return_value
    mock_db.execute_query.return_value = [
        {"balance": "0.05"},
    ]
    mock_db.fetch_records.return_value = [{"id": 1, "type": "addition", "cost": "0.1"}]

    calculation_request = {
        "operation": "addition",
        "operands": [1, 3, 2],
    }

    response = client.post(
        "/api/v1/calculations/new",
        json=calculation_request,
        headers=auth_header,
    )

    assert response.status_code == 402
    json_data = response.get_json()
    assert json_data == {"error": "Insufficient funds"}


@patch("routes.calculation.DBService")
def test_run_calc_unknown_op(mock_db_service, client, auth_header):

    mock_db = mock_db_service.return_value.__enter__.return_value
    mock_db.execute_query.return_value = [
        {"balance": "0.05"},
    ]

    mock_db.fetch_records.return_value = []

    calculation_request = {
        "operation": "modulo",
        "operands": [7, 2],
    }

    response = client.post(
        "/api/v1/calculations/new",
        json=calculation_request,
        headers=auth_header,
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data == {"error": "Operation 'modulo' not known"}


def test_run_calc_required_fields(client, auth_header):

    calculation_request1 = {
        "operation": "square_root",
    }

    response1 = client.post(
        "/api/v1/calculations/new",
        json=calculation_request1,
        headers=auth_header,
    )

    assert response1.status_code == 400
    assert response1.get_json() == {"error": "Field 'operands' is required"}

    calculation_request2 = {
        "operands": [1, 2, 3],
    }

    response2 = client.post(
        "/api/v1/calculations/new",
        json=calculation_request2,
        headers=auth_header,
    )

    assert response2.status_code == 400
    assert response2.get_json() == {"error": "Field 'operation' is required"}

    calculation_request3 = {}

    response3 = client.post(
        "/api/v1/calculations/new",
        json=calculation_request3,
        headers=auth_header,
    )

    assert response3.status_code == 400
    assert response3.get_json() == {"error": "Field 'operation' is required"}
