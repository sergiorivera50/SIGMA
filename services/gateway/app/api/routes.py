from flask import Blueprint, request, current_app
import requests
from gateway.app.util.decorators import authorized

bp = Blueprint("auth", __name__)


@bp.route("/deploy", methods=["POST"])
@authorized
def deploy():
    registry_host = current_app.config.get("REGISTRY_SVC_HOST")
    register_response = requests.post(f"{registry_host}/register", data=request.form, files=request.files)
    return register_response.text, 200


@bp.route("/<model_id>/predict", methods=["POST"])
@authorized
def predict(model_id):
    dev_host = current_app.config.get("INFERENCE_SVC_HOST")
    prod_host = f"http://{model_id}.default.svc.cluster.local:3000"
    backend_host = dev_host if current_app.debug else prod_host
    response = requests.post(f"{backend_host}/predict", json=request.get_json())
    return response.json()
