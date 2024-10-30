import functools
from datetime import datetime, timedelta

import jwt
from flask import request, jsonify

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS


class JWTService:

    def __init__(
        self,
        secret_key=JWT_SECRET,
        algorithm=JWT_ALGORITHM,
        expiration_hours=JWT_EXPIRATION_HOURS,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def generate_token(self, user_id):
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token):
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}


def jwt_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.split(" ")[1]

        decoded = JWTService().verify_token(token)
        if "error" in decoded:
            return jsonify(decoded), 401

        return f(*args, **kwargs)

    return wrapper
