from flask import current_app


def make_response_class(response):
    return current_app.response_class(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )


def isAuthType(header, auth_type="Basic"):
    return header.startswith(f"{auth_type} ")
