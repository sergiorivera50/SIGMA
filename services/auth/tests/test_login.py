from auth.tests.conftest import AuthActions, DataActions


def test_login_missing_credentials(client):
    response = AuthActions(client).login(auth_type=None)
    assert response.status_code == 401
    assert response.data == b"Missing Credentials"


def test_login_invalid_authorization_type(client):
    response = AuthActions(client).login(auth_type="Bearer")
    assert response.status_code == 400
    assert response.data == b"Invalid Authorization Type"


def test_login_invalid_credentials(client):
    response = AuthActions(client).login("invalid_email", "invalid_password")
    assert response.status_code == 401
    assert response.data == b"Invalid Credentials"


def test_login_valid_credentials(app, client):
    valid_email, valid_password = DataActions(app).fetch_credentials()
    response = AuthActions(client).login(valid_email, valid_password)
    assert response.status_code == 200
