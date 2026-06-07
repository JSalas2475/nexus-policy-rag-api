import logging

from flask import Flask

logger = logging.getLogger(__name__)

_rag_pipeline = None


def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        from app.config import settings
        from app.rag.pipeline import RAGPipeline

        _rag_pipeline = RAGPipeline(settings)
    return _rag_pipeline


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"

    from app.routes.chat import chat_bp
    from app.routes.health import health_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(health_bp)

    @app.route("/")
    def index():
        from flask import render_template

        return render_template("index.html")

    return app
