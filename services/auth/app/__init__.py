from flask import Flask
import os


def create_app(test_config=None):
    app = Flask(__name__)

    # Configure application variables
    if test_config is None:
        app.config.from_mapping(
            JWT_SECRET=os.environ.get("JWT_SECRET"),
            DATABASE=os.environ.get("DATABASE") or f"{os.path.abspath('data/auth.db')}"
        )
    else:
        app.config.update(test_config)

    assert app.config.get("JWT_SECRET"), "JWT secret has not been configured"

    # Register database commands
    from auth.app.db import init_app
    init_app(app)

    # Register endpoints
    from auth.app.api.routes import bp as routes
    app.register_blueprint(routes)

    return app
