from flask import Blueprint, request, current_app
import requests
from requests.auth import HTTPBasicAuth

bp = Blueprint("auth", __name__)


@bp.route("/deploy", methods=["POST"])
def deploy():
    if not request.headers.get("Authorization"):
        return "Did not send credentials", 401

    auth_host = current_app.config.get("AUTH_SVC_HOST")
    login_response = requests.post(f"{auth_host}/login",
                                   auth=HTTPBasicAuth(request.authorization.username,
                                                      request.authorization.password))
    if login_response.status_code != 200:
        return "Unauthorized", 401

    registry_host = current_app.config.get("REGISTRY_SVC_HOST")
    register_response = requests.post(f"{registry_host}/register", data=request.form, files=request.files)
    return register_response.text, 200


@bp.route("/<model_id>/predict", methods=["POST"])
def predict(model_id):
    dev_host = current_app.config.get("INFERENCE_SVC_HOST")
    prod_host = f"http://{model_id}.default.svc.cluster.local:3000"
    backend_host = dev_host if current_app.debug else prod_host
    response = requests.post(f"{backend_host}/predict", json=request.get_json())
    return response.json()
