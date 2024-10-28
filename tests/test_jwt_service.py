import jwt

from services.jwt_service import JWTService


def test_generate_token():

    jwt_service = JWTService(secret_key="TEST SECRET", expiration_hours=1)
    token = jwt_service.generate_token(user_id=999)

    # decode the token to verify its contents
    decoded_token = jwt.decode(token, "TEST SECRET", algorithms=["HS256"])
    assert decoded_token["user_id"] == 999
    assert "exp" in decoded_token


def test_verify_token():

    jwt_service = JWTService(secret_key="TEST SECRET", expiration_hours=1)
    token1 = jwt_service.generate_token(user_id=999)
    token2 = jwt_service.generate_token(user_id=-1)
    token3 = jwt_service.generate_token(user_id="TEST USER")

    decoded_token1 = jwt_service.verify_token(token1)
    decoded_token2 = jwt_service.verify_token(token2)
    decoded_token3 = jwt_service.verify_token(token3)

    assert decoded_token1["user_id"] == 999
    assert decoded_token2["user_id"] == -1
    assert decoded_token3["user_id"] == "TEST USER"


def test_verify_expired_token():

    # setting expiration hours to -1 should create an expired token
    jwt_service = JWTService(secret_key="TEST SECRET", expiration_hours=-1)
    token = jwt_service.generate_token(user_id=999)

    result = jwt_service.verify_token(token)
    assert result == {"error": "Token has expired"}
