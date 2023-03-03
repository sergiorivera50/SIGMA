from functools import wraps
from flask import request, current_app, g
import jwt

from auth.app.util.headers import isAuthType


def requires_auth(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Enforce "Authorization" header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return "Missing Credentials", 401

            # Ensure only "Bearer" auth type is allowed
            if not isAuthType(auth_header, "Bearer"):
                return "Invalid Authorization Type", 400

            # Extract <token> from Bearer header
            token = auth_header.split(" ")[1]

            # Attempt to decode JWT using secret
            try:
                decoded = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            except jwt.exceptions.DecodeError:
                return "Not Authorized", 403
            except Exception as e:
                print(f"Unexpected Error: {e}")
                return "Unexpected Error Occured", 500

            if role and not decoded.get("role") == role:
                return "Not Authorized", 403

            g.user = decoded

            return f(*args, **kwargs)
        return decorated_function
    return decorator
