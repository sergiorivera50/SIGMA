from flask import Flask
import os


def create_app(test_config=None):
    app = Flask(__name__)

    # Configure application variables
    if test_config is None:
        app.config.from_mapping(
            AUTH_SVC_HOST=os.environ.get("AUTH_SVC_HOST"),
            REGISTRY_SVC_HOST=os.environ.get("REGISTRY_SVC_HOST"),
            INFERENCE_SVC_HOST=os.environ.get("INFERENCE_SVC_HOST")  # optional: only used in dev
        )
    else:
        app.config.update(test_config)

    assert app.config.get("AUTH_SVC_HOST"), "Authorization service has not been specified"
    assert app.config.get("REGISTRY_SVC_HOST"), "Registry service has not been specified"

    # Register endpoints
    from gateway.app.api.routes import bp as routes
    app.register_blueprint(routes)

    return app
