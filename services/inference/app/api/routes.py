import numpy as np
from flask import Blueprint, current_app, request, jsonify
from inference.app.util.registry import load_model


bp = Blueprint("auth", __name__)


@bp.route("/predict", methods=["POST"])
def predict():
    model_id = current_app.config.get("MODEL_ID")
    model = load_model(model_id)
    input_data = request.get_json()
    current_app.logger.info(f"Incoming inference with input size {np.array(input_data).shape}.")
    prediction = model.predict(input_data)
    current_app.logger.info(f"Prediction complete with output size {prediction.shape}.")
    return jsonify({
        "result": prediction.tolist()
    })
