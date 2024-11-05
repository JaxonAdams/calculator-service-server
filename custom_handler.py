import os
import sys
import json
import traceback
from serverless_wsgi import handle_request


# Import the application defined in the generated handler
def load_app():
    try:
        from app import app
        return app
    except Exception as e:
        print(f"Failed to load app: {e}")
        traceback.print_exc()
        raise


def handler(event, context):
    """Lambda event handler, invokes the WSGI wrapper and handles command invocation."""
    try:
        app = load_app()
        return handle_request(app, event, context)
    except Exception as e:
        print(f"Error handling request: {e}")
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error", "error": str(e)})
        }
