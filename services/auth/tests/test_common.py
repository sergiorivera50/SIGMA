from auth.tests.conftest import AuthActions


def test_config(app):
    assert app.testing


def test_validate_missing_credentials(client):
    response = AuthActions(client).validate(auth_type=None)
    assert response.status_code == 401
    assert response.data == b"Missing Credentials"


def test_validate_invalid_authorization_type(client):
    response = AuthActions(client).validate(auth_type="Basic")
    assert response.status_code == 400
    assert response.data == b"Invalid Authorization Type"


def test_validate_invalid_credentials(client):
    response = AuthActions(client).validate("invalid_token")
    assert response.status_code == 403
    assert response.data == b"Not Authorized"
