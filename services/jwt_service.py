import functools
from datetime import datetime, timedelta, UTC

import jwt
from flask import request, jsonify

from services.db_service import DBService
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS


class JWTService:
    """Service class for generating and verifying JWT tokens."""

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
        """Generate a JWT token for the provided user ID."""

        payload = {
            "user_id": user_id,
            "exp": datetime.now(UTC) + timedelta(hours=self.expiration_hours),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_admin_token(self, created_by, description):
        """Generate a JWT token for an admin API key."""

        payload = {
            "role": "admin",
            "created_by": created_by,
            "description": description,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token):
        """Verify the provided token and return the decoded payload."""
        
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}


def jwt_required(f):
    """Decorator to require a valid user JWT token for a route."""
    
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


def admin_protected(f):
    """Decorator to require an admin API key for a route."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.split(" ")[1]

        decoded = JWTService().verify_token(token)
        if "error" in decoded:
            return jsonify(decoded), 401

        if "role" not in decoded or decoded["role"] != "admin":
            return (
                jsonify(
                    {
                        "error": "An admin API key is required to use this endpoint. Please contact an administrator if you need a key."
                    }
                ),
                403,
            )

        with DBService() as db:
            results = db.fetch_records(
                "admin_key",
                conditions={"api_key": token, "deleted": False},
            )

            if not results:
                return jsonify({"error": "Invalid or inactive API key."}), 401

        return f(*args, **kwargs)

    return wrapper
