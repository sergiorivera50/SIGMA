import jwt
from flask import Blueprint, request, current_app

from auth.app.db import get_db
from auth.app.util.tokens import createJWT
from auth.app.util.headers import isAuthType

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    """Log in a user via Basic Authorization by creating an encoded JWT."""

    # Enforce "Authorization" header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return "Missing Credentials", 401

    # Ensure only "Basic" auth type is allowed
    if not isAuthType(auth_header, "Basic"):
        return "Invalid Authorization Type", 400

    # Fetch user from data (via email field)
    auth = request.authorization
    cursor = get_db()
    result = cursor.execute(
        "SELECT email, password FROM user WHERE email=?",
        (auth.username,)
    ).fetchone()

    # Authenticate user (if provided details match data values)
    if result is not None:
        email, password = result[0], result[1]
        if auth.username == email and auth.password == password:
            return createJWT(auth.username, current_app.config["JWT_SECRET"])
        else:
            return "Invalid Credentials", 401
    else:
        return "Invalid Credentials", 401


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
