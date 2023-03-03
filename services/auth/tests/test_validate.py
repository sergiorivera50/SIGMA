from auth.tests.conftest import DataActions, AuthActions


def test_validate_valid_credentials(app, client):
    # Log in with valid username and password
    valid_email, valid_password = DataActions(app).fetch_credentials()
    auth = AuthActions(client)
    login_response = auth.login(valid_email, valid_password)
    token = login_response.data.decode()

    # Verify token in the /validate endpoint
    response = auth.validate(token)
    assert response.status_code == 200


def test_validate_missing_token(client):
    response = AuthActions(client).validate(auth_type=None)
    assert response.status_code == 401
    assert response.data == b"Missing Credentials"


def test_validate_invalid_authorization_type(client):
    response = AuthActions(client).validate(auth_type="Basic")
    assert response.status_code == 400
    assert response.data == b"Invalid Authorization Type"


def test_validate_invalid_token(client):
    response = AuthActions(client).validate("invalid_token")
    assert response.status_code == 403
    assert response.data == b"Not Authorized"
