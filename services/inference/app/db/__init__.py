import gzip
import json

from flask import g, current_app
import pymongo
from pymongo.server_api import ServerApi
from gridfs import GridFS
import redis


def get_db():
    if "data" not in g:
        client = pymongo.MongoClient(
            current_app.config.get("MONGODB_HOST"),
            server_api=ServerApi('1')
        )
        g.db = client[current_app.config.get("DATABASE")]
    return g.db


def get_cache():
    return redis.Redis(
        host=current_app.config.get("REDIS_HOST"),
        port=current_app.config.get("REDIS_PORT"),
        db=0)


def init_cache(model_id):
    from inference.app.util.registry import request_model, request_weights
    cache = get_cache()
    metadata = request_model(model_id)
    compressed_weights = request_weights(model_id)
    cache.set(f"{model_id}:metadata", json.dumps(metadata))
    cache.set(f"{model_id}:weights", compressed_weights)


def from_cache(key):
    cache = get_cache()
    if cache.exists(key):
        return cache.get(key)
    else:
        raise AttributeError(f"Key {key} not found in cache!")


def to_cache(key, value):
    cache = get_cache()
    cache.set(key, value)


def get_fs():
    return GridFS(get_db())
