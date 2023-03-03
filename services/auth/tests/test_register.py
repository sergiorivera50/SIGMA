from auth.tests.conftest import AuthActions, DataActions
from faker import Faker
import secrets


def test_register_missing_token(client):
    response = AuthActions(client).register(auth_type=None)
    assert response.status_code == 401
    assert response.data == b"Missing Credentials"


def test_register_invalid_authorization_type(client):
    response = AuthActions(client).register(auth_type="Basic")
    assert response.status_code == 400
    assert response.data == b"Invalid Authorization Type"


def test_register_invalid_token(client):
    response = AuthActions(client).register(token="invalid_token")
    assert response.status_code == 403
    assert response.data == b"Not Authorized"


def test_register_empty_data(app, client):
    authorized_user = DataActions(app).fetch_credentials(role="superuser")
    login_response = AuthActions(client).login(*authorized_user)
    token = login_response.data.decode()
    response = AuthActions(client).register(token=token)
    assert response.status_code == 500
    assert response.data == b"Unexpected Error Occurred"


def test_register_missing_data(app, client):
    authorized_user = DataActions(app).fetch_credentials(role="superuser")
    login_response = AuthActions(client).login(*authorized_user)
    token = login_response.data.decode()
    response = AuthActions(client).register(token=token, data={
        "irrelevant_field1": "value", "irrelevant_field2": "value"
    })
    assert response.status_code == 400
    assert response.data == b"Email and password are required."


def test_register_invalid_role(app, client):
    unauthorized_user = DataActions(app).fetch_credentials(role="regular")
    token = AuthActions(client).login(*unauthorized_user)
    response = AuthActions(client).register(token=token, data={
        "email": "new@email.com", "password": "123456789"
    })
    assert response.status_code == 403
    assert response.data == b"Not Authorized"


def test_register_valid(app, client):
    authorized_user = DataActions(app).fetch_user("superuser")
    login_response = AuthActions(client).login(email=authorized_user["email"], password=authorized_user["password"])
    token = login_response.data.decode()

    email = Faker().email()
    password = secrets.token_urlsafe(16)
    response = AuthActions(client).register(token=token, data={
        "email": email, "password": password
    })
    assert response.status_code == 201
    assert response.data == b"User created successfully"

    created_user = DataActions(app).fetch_user(email)
    assert created_user["email"] == email \
           and created_user["password"] == password \
           and created_user["role"] == "regular"
