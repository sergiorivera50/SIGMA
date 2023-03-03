import json
import os
import tempfile
from base64 import b64encode

import pytest

from auth.app import create_app
from auth.app.db import init_db, get_db, close_db


@pytest.fixture()
def app():
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()

    # Create the app instance with testing enabled
    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
        "JWT_SECRET": "test"
    })

    with app.app_context():
        # Initialise the database
        init_db()

        # Populate the database with mock data
        with open(os.path.join(os.path.dirname(__file__), "values.sql"), "rb") as f:
            query = f.read().decode("utf8")
        get_db().executescript(query)

        yield app

        # Close the database
        close_db()

    # Cleanup the temporary file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


class DataActions(object):
    def __init__(self, app):
        self._app = app

    def fetch_credentials(self, role="regular"):
        with self._app.app_context():
            cursor = get_db().cursor()
            cursor.execute(
                "SELECT email, password FROM user WHERE role=? LIMIT 1", (role,)
            )
            res = cursor.fetchone()
            if res:
                email, password = res[0], res[1]
                return email, password
            else:
                raise Exception(f"No user available with role {role}")

    def fetch_user(self, identifier):
        with self._app.app_context():
            cursor = get_db().cursor()
            cursor.execute(
                "SELECT * FROM user WHERE role=? OR email=? LIMIT 1",
                (identifier, identifier),
            )
            res = cursor.fetchone()
            if res:
                return res
            else:
                raise Exception(f"No user available with role or username {identifier}")


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="", password="", auth_type="Basic"):
        if auth_type is None:
            return self._client.post("/login")
        credentials = b64encode(str.encode(f"{email}:{password}")).decode("utf-8")
        return self._client.post("/login", headers={"Authorization": f"{auth_type} {credentials}"})

    def validate(self, token="", auth_type="Bearer"):
        if auth_type is None:
            return self._client.post("/validate")
        return self._client.post("/validate", headers={"Authorization": f"{auth_type} {token}"})

    def register(self, token="", auth_type="Bearer", data=None):
        if auth_type is None:
            return self._client.post("/register", data=json.dumps(data))
        headers = {
            "Authorization": f"{auth_type} {token}",
            "Content-Type": "application/json"
        }
        return self._client.post("/register", headers=headers, data=json.dumps(data))
