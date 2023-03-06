import logging

from flask import Flask
import os


logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def create_app(test_config=None):
    app = Flask(__name__)

    app.logger.setLevel(logging.INFO)

    # Configure application variables
    if test_config is None:
        app.config.from_mapping(
            MODEL_ID=os.environ.get("MODEL_ID"),
            REGISTRY_SVC_HOST=os.environ.get("REGISTRY_SVC_HOST"),
            MONGODB_HOST=os.environ.get("MONGODB_HOST"),
            DATABASE=os.environ.get("DATABASE") or "sigma",
            REDIS_HOST=os.environ.get("REDIS_HOST"),
            REDIS_PORT=os.environ.get("REDIS_PORT") or 6379
        )
    else:
        app.config.update(test_config)

    assert app.config.get("MODEL_ID"), "Model identifier has not been configured"
    assert app.config.get("REGISTRY_SVC_HOST"), "Registry service host has not been configured"
    assert app.config.get("MONGODB_HOST"), "MongoDB host has not been configured"
    assert app.config.get("DATABASE"), "Database has not been selected"
    assert app.config.get("REDIS_HOST"), "Redis host has not been configured"

    with app.app_context():
        # Register endpoints
        from inference.app.api.routes import bp as routes
        app.register_blueprint(routes)

        # Store the model into cache
        from inference.app.db import init_cache
        init_cache(app.config.get("MODEL_ID"))

    return app
