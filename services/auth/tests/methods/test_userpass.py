from auth.tests.conftest import AuthActions, DataActions


def test_userpass_login_missing_credentials(client):
    response = AuthActions(client).userpass_login(auth_type=None)
    assert response.status_code == 401
    assert response.data == b"Missing Credentials"


def test_userpass_login_invalid_authorization_type(client):
    response = AuthActions(client).userpass_login(auth_type="Bearer")
    assert response.status_code == 400
    assert response.data == b"Invalid Authorization Type"


def test_userpass_login_invalid_credentials(client):
    response = AuthActions(client).userpass_login("invalid_email", "invalid_password")
    assert response.status_code == 401
    assert response.data == b"Invalid Credentials"


def test_userpass_login_valid_credentials(app, client):
    valid_email, valid_password = DataActions(app).fetch_userpass_credentials()
    response = AuthActions(client).userpass_login(valid_email, valid_password)
    assert response.status_code == 200


def test_validate_valid_userpass_credentials(app, client):
    # Log in with valid username and password
    valid_email, valid_password = DataActions(app).fetch_userpass_credentials()
    auth = AuthActions(client)
    login_response = auth.userpass_login(valid_email, valid_password)
    token = login_response.data.decode()

    # Verify token in the /validate endpoint
    response = auth.validate(token)
    assert response.status_code == 200

