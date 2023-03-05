import gzip
import json
import os
import requests
from flask import current_app
from inference.app.db import get_fs, get_cache, from_cache, to_cache
import tempfile
from tensorflow import keras


def request_weights(model_id):
    """ Fetches the model weights directly from GridFS """
    weights_file = get_fs().find_one({"filename": model_id + ".h5"})
    return weights_file.read()


def request_model(model_id):
    """ Fetches the model metadata from the registry service """
    registry_host = current_app.config.get("REGISTRY_SVC_HOST")
    return requests.get(f"{registry_host}/fetch?id={model_id}").json()


def fetch_model(model_id):
    """ Returns model metadata from cache (requests resource if not present) """
    cache = get_cache()
    cache_key = f"{model_id}:metadata"
    if cache.exists(cache_key):
        current_app.logger.info(f"Model metadata found in cache with key {cache_key}")
        metadata = json.loads(cache.get(cache_key))
    else:
        current_app.logger.info(f"Model metadata not present in cache with key {cache_key}")
        metadata = request_model(model_id)
        cache.set(cache_key, json.dumps(metadata))
    assert type(metadata) is dict
    return metadata


def fetch_weights(model_id):
    """ Returns model weights from cache (requests resource if not present) """
    weights_key = f"{model_id}:weights"
    try:
        compressed_weights = from_cache(weights_key)
        current_app.logger.info(f"Model weights found in cache with key {weights_key}")
    except AttributeError:
        compressed_weights = request_weights(model_id)
        current_app.logger.info(f"Model weights not found in cache with key ({weights_key})")
        to_cache(weights_key, compressed_weights)
    return gzip.decompress(compressed_weights)


def load_weights(model, model_id):
    """ Loads weights into a model via temporary file """
    weights_data = fetch_weights(model_id)
    current_app.logger.info(f"Weights data: {weights_data}")

    # Create a temporary file-like object for the weights data
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(weights_data)
        weights_file_path = f.name

    current_app.logger.info(f"Weights path: {weights_file_path}")
    # Load the model weights from the temporary file
    model.load_weights(weights_file_path)

    # Delete the temporary file
    os.unlink(weights_file_path)

    return model


def load_model(model_id):
    """ Constructs a compiled model from model_id """
    current_app.logger.info(f"Attempting to compile model...")
    metadata = fetch_model(model_id)
    model = keras.models.model_from_json(
        metadata.get("architecture")
    )
    model = load_weights(model, model_id)
    model.compile(
        loss=metadata.get("loss_fn"),
        optimizer=metadata.get("optimizer"),
        metrics=metadata.get("metrics")
    )
    current_app.logger.info(f"Model successfully compiled.")
    return model
