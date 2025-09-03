"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
from flask import Flask
from waitress import serve

def create_app(config_obj) -> Flask:
    """Application factory for the Qalita CLI UI."""
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "public"),
        static_url_path="/static",
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    )

    app.config["QALITA_CONFIG_OBJ"] = config_obj

    # Register blueprints
    from qalita.web.blueprints.dashboard import bp as dashboard_bp
    from qalita.web.blueprints.context import bp as context_bp
    from qalita.web.blueprints.agents import bp as agents_bp
    from qalita.web.blueprints.sources import bp as sources_bp
    from qalita.web.blueprints.studio import bp as studio_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(context_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(sources_bp, url_prefix="/sources")
    app.register_blueprint(studio_bp, url_prefix="/studio")

    return app


def run_dashboard_ui(config_obj, host: str = "localhost", port: int = 7070):
    app = create_app(config_obj)
    url = f"http://{host}:{port}"
    print(f"Qalita CLI UI is running. Open {url}")
    serve(app, host=host, port=port)
