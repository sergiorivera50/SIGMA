import jwt
from flask import Blueprint, request, current_app

from auth.app.util.headers import isAuthType

bp = Blueprint("common", __name__)


@bp.route("/validate", methods=["POST"])
def validate():
    """Validate an encoded JWT."""

    # Enforce "Authorization" header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return "Missing Credentials", 401

    # Ensure only "Bearer" auth type is allowed
    if not isAuthType(auth_header, "Bearer"):
        return "Invalid Authorization Type", 400

    token = auth_header.split(" ")[1]  # select "<token>" from "Bearer <token>"

    # Attempt to decode JWT using secret
    try:
        decoded = jwt.decode(
            token, current_app.config["JWT_SECRET"], algorithms=["HS256"]
        )
    except jwt.exceptions.DecodeError:
        return "Not Authorized", 403
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"Unexpected Error Occured", 500
    return decoded, 200
