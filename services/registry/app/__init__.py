from flask import Flask
import os
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def create_app(test_config=None):
    app = Flask(__name__)

    # Configure application variables
    if test_config is None:
        app.config.from_mapping(
            MONGODB_HOST=os.environ.get("MONGODB_HOST"),
            DATABASE=os.environ.get("DATABASE") or "sigma"
        )
    else:
        app.config.update(test_config)

    assert app.config.get("MONGODB_HOST"), "MongoDB host has not been configured"
    assert app.config.get("DATABASE"), "Database has not been selected"

    # Register endpoints
    from registry.app.api.routes import bp as routes
    app.register_blueprint(routes)

    return app
