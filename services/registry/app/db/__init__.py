from flask import g, current_app
import pymongo
from pymongo.server_api import ServerApi
from gridfs import GridFS


def get_db():
    if "data" not in g:
        client = pymongo.MongoClient(
            current_app.config.get("MONGODB_HOST"),
            server_api=ServerApi('1')
        )
        g.db = client[current_app.config.get("DATABASE")]
    return g.db


def get_fs():
    return GridFS(get_db())
