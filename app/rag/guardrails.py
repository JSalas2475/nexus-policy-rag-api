import re

from app.rag.generation import REFUSAL_MESSAGE, extract_citations, truncate_words
from app.rag.retrieval import RetrievedChunk

OFF_TOPIC_PATTERNS = [
    r"\bweather\b",
    r"\brecipe\b",
    r"\bfootball\b",
    r"\bstock price\b",
    r"\bcapital of\b",
]


def apply_guardrails(
    question: str,
    chunks: list[RetrievedChunk],
    raw_answer: str,
    score_threshold: float,
    max_answer_words: int,
) -> tuple[str, list[dict], bool]:
    if _is_off_topic_question(question):
        return REFUSAL_MESSAGE, [], True

    max_score = max((chunk.similarity_score for chunk in chunks), default=0.0)
    if not chunks or max_score < score_threshold:
        return REFUSAL_MESSAGE, [], True

    answer = truncate_words(raw_answer, max_answer_words)
    citations = extract_citations(answer, chunks)
    citations = _validate_citations(citations, chunks)

    if not citations:
        chunk = chunks[0]
        answer = f"{answer} [{chunk.doc_id}: {chunk.section}]"
        citations = [
            {
                "doc_id": chunk.doc_id,
                "title": chunk.title,
                "section": chunk.section,
                "snippet": chunk.snippet,
                "source_path": chunk.source_path,
            }
        ]

    return answer, citations, False


def _is_off_topic_question(question: str) -> bool:
    lowered = question.lower()
    return any(re.search(pattern, lowered) for pattern in OFF_TOPIC_PATTERNS)


def _validate_citations(
    citations: list[dict], chunks: list[RetrievedChunk]
) -> list[dict]:
    valid_doc_ids = {chunk.doc_id for chunk in chunks}
    return [citation for citation in citations if citation["doc_id"] in valid_doc_ids]
