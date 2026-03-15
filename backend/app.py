"""
app.py – Flask application factory for Compass Outlaw backend.
"""

from flask import Flask

from backend.api.routes import api_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    return app


if __name__ == "__main__":  # pragma: no cover
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    create_app().run(debug=debug)
