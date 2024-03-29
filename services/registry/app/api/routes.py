import gzip

import kubernetes
from flask import Blueprint, request, jsonify, current_app
from registry.app.db import get_db, get_fs
from bson.objectid import ObjectId
from registry.app.utils.kubernetes import parse_manifest

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    model_name = request.form['model_name']
    arch_file = request.files['arch_file']
    weights_file = request.files['weights_file']
    loss_fn = request.form['loss_fn']
    optimizer = request.form['optimizer']
    metrics = request.form['metrics']

    metadata = {
        'model_name': model_name,
        'loss_fn': loss_fn,
        'optimizer': optimizer,
        'metrics': metrics.split(',')
    }
    model_id = get_db().models.insert_one(metadata).inserted_id
    model_id = str(model_id)

    # Save the files to GridFS
    fs = get_fs()
    fs.put(arch_file, filename=model_id + ".json")
    weigths_data = weights_file.read()
    fs.put(gzip.compress(weigths_data), filename=model_id + ".h5")

    # Deploy InferenceBackend CRD resource
    if not current_app.debug:
        current_app.logger.info(f"Deploying InferenceBackend resource for model id {model_id}")
        kubernetes.config.load_incluster_config()
        inference_backend_manifest = parse_manifest("inferencebackend.yaml",
                                                    model_name=model_name.replace('_', '-'),
                                                    model_id=model_id)
        api = kubernetes.client.CustomObjectsApi()
        api.create_namespaced_custom_object(body=inference_backend_manifest,
                                            namespace="default",
                                            group="inference.sigma.com",
                                            version="v1",
                                            plural="inferencebackends")

    # Return the Object ID to the client
    return model_id, 201


@bp.route("/fetch", methods=["GET"])
def fetch():
    model_id = request.args.get("id")

    # Find the model architecture file in GridFS
    arch_file = get_fs().find_one({'filename': model_id + ".json"})
    if arch_file is None:
        return f"Architecture file for {model_id} not found in GridFS", 400

    # Read the model architecture JSON string
    arch_data = arch_file.read().decode()

    # Get the model metadata from the database
    metadata = get_db().models.find_one({'_id': ObjectId(model_id)})

    return jsonify({
        "model_id": model_id,
        "model_name": metadata["model_name"],
        "architecture": arch_data,
        "loss_fn": metadata["loss_fn"],
        "optimizer": metadata["optimizer"],
        "metrics": metadata["metrics"]
    }), 200
