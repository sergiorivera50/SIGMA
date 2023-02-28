import datetime
import jwt


def createJWT(username, role, secret, algorithm="HS256"):
    return jwt.encode({
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
        "username": username,
        "role": role
    }, secret, algorithm)
