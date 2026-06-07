from flask import Blueprint, jsonify, request

from app import get_rag_pipeline

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    pipeline = get_rag_pipeline()
    if not pipeline.is_index_loaded():
        return jsonify({"error": "RAG index not loaded. Run scripts/ingest.py first."}), 503

    response = pipeline.answer(question)
    return jsonify(
        {
            "answer": response.answer,
            "citations": response.citations,
            "latency_ms": response.latency_ms,
            "refused": response.refused,
        }
    )
