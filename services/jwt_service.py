from datetime import datetime, timedelta

import jwt

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
