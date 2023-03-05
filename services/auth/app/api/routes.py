from flask import Blueprint, request, current_app, g

from auth.app.db import get_db
from auth.app.util.tokens import createJWT
from auth.app.util.headers import isAuthType
from auth.app.util.decorators import requires_auth

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    """ Log in a user via Basic Authorization by creating an encoded JWT. """

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
        "SELECT email, password, role FROM user WHERE email=?",
        (auth.username,)
    ).fetchone()

    # Authenticate user (if provided details match data values)
    if result is not None:
        email, password, role = result[0], result[1], result[2]
        if auth.username == email and auth.password == password:
            return createJWT(auth.username, role, current_app.config["JWT_SECRET"])
        else:
            return "Invalid Credentials", 401
    else:
        return "Invalid Credentials", 401


@bp.route("/validate", methods=["POST"])
@requires_auth()
def validate():
    """ Decode a JWT with secret via Bearer token. """
    return g.user, 200


@bp.route("/register", methods=["POST"])
@requires_auth(role="superuser")
def register():
    """ Register a new user. """
    try:
        body = request.get_json()
        email, password = body.get("email"), body.get("password")

        if not email or not password:
            return "Email and password are required.", 400

        cursor = get_db()
        cursor.execute("INSERT INTO user (email, password, role) VALUES (?, ?, ?)", (email, password, "regular"))
        cursor.commit()

        return "User created successfully", 201
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"Unexpected Error Occurred", 500
