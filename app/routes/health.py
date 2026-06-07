from flask import Blueprint, jsonify

from app.config import settings

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    index_loaded = False
    try:
        from app.rag.vectorstore import VectorStoreManager

        manager = VectorStoreManager(
            persist_dir=settings.chroma_persist_dir,
            embedding_model_name=settings.embedding_model,
        )
        index_loaded = manager.is_loaded()
    except Exception:
        index_loaded = False

    return jsonify(
        {
            "status": "ok",
            "index_loaded": index_loaded,
            "model": settings.groq_model,
            "embedding_model": settings.embedding_model,
        }
    )
