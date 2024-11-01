"""Generate a new admin API key and store it in the database."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.db_service import DBService
from services.jwt_service import JWTService

created_by = input('\nEnter a value for "created_by" >> ')
description = input('\nEnter a value for "description" >> ')
print()

token = JWTService().generate_admin_token(created_by, description)

print(f"\nYour new admin key:\n{token}")
print("\nStoring your key in the database...\n")

with DBService() as db:
    db.insert_record(
        "admin_key",
        {
            "api_key": token,
            "created_by": created_by or None,
            "description": description or None,
        },
    )

print("Done!")
