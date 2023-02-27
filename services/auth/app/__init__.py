from flask import Flask
import os


def create_app(test_config=None):
    app = Flask(__name__)

    # Configure application variables
    if test_config is None:
        app.config.from_mapping(
            JWT_SECRET=os.environ.get("JWT_SECRET") or "apple",
            DATABASE=os.environ.get("DATABASE") or f"{os.path.abspath('data/auth.db')}"
        )
    else:
        app.config.update(test_config)

    # Register database commands
    from auth.app.db import init_app
    init_app(app)

    # Register common endpoints
    from auth.app.api.common.routes import bp as common
    app.register_blueprint(common)

    # Register authentication methods
    from auth.app.api.methods.userpass.routes import bp as userpass
    app.register_blueprint(userpass)

    return app
