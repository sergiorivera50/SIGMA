import functools
from flask import request, current_app
import requests
from gateway.app.util.http import make_response_class


def authorized(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_host = current_app.config.get("AUTH_SVC_HOST")
        response = requests.post(f"{auth_host}/validate", headers=request.headers)
        if response.status_code != 200:
            return response.content, response.status_code, response.headers.items()
        return f(*args, **kwargs)
    return decorated_function


def proxy(hostname, route=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Build the URL for the destination host
            host = current_app.config.get(hostname)
            path = request.path if route is None else route
            url = f'{host}{path}'

            # Forward the request to the destination host
            response = requests.request(
                method=request.method,
                url=url,
                headers=request.headers,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False
            )

            return make_response_class(response)
        return wrapper
    return decorator
