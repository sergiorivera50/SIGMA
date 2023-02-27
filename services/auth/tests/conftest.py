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

    def fetch_userpass_credentials(self):
        with self._app.app_context():
            res = get_db().execute("SELECT email, password FROM user LIMIT 1").fetchone()
            email, password = res[0], res[1]
            return email, password


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def userpass_login(self, email="", password="", auth_type="Basic"):
        if auth_type is not None:
            credentials = b64encode(str.encode(f"{email}:{password}")).decode("utf-8")
            return self._client.post("/method/userpass/login", headers={"Authorization": f"{auth_type} {credentials}"})
        else:
            return self._client.post("/method/userpass/login")

    def validate(self, token="", auth_type="Bearer"):
        if auth_type is not None:
            return self._client.post("/validate", headers={"Authorization": f"{auth_type} {token}"})
        else:
            return self._client.post("/validate")
