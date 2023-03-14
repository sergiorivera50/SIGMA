from flask import Blueprint, request, current_app
import requests
from gateway.app.util.decorators import authorized, proxy
from gateway.app.util.http import make_response_class

bp = Blueprint("auth", __name__)


@bp.route("/ping", methods=["GET"])
def ping():
    return "pong", 200


@bp.route("/deploy", methods=["POST"])
@authorized
def deploy():
    registry_host = current_app.config.get("REGISTRY_SVC_HOST")
    register_response = requests.post(f"{registry_host}/register", data=request.form, files=request.files)
    return register_response.text, 200


@bp.route("/<model_id>/predict", methods=["POST"])
@authorized
def predict(model_id):
    backend_host = current_app.config.get("INFERENCE_SVC_HOST")
    if not current_app.debug:
        registry_host = current_app.config.get("REGISTRY_SVC_HOST")
        fetch_response = requests.get(f"{registry_host}/fetch?id={model_id}")
        if fetch_response.status_code != 200:
            return make_response_class(fetch_response)
        model_name = fetch_response.json().get("model_name")
        backend_host = f"http://{model_name}.default.svc.cluster.local:3000"
    response = requests.post(f"{backend_host}/predict", json=request.get_json())
    return response.json()


@bp.route("/login", methods=["POST"])
@proxy("AUTH_SVC_HOST")
def login():
    pass
