import functools
from flask import request, current_app
import requests
import os


def authorized(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_host = current_app.config.get("AUTH_SVC_HOST")
        response = requests.post(f"{auth_host}/validate", headers=request.headers)
        if response.status_code != 200:
            return response.content, response.status_code, response.headers.items()
        return f(*args, **kwargs)
    return decorated_function
