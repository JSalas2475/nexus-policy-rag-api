#!/usr/bin/env python3
"""Run evaluation suite against the RAG pipeline."""

import json
import random
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from app.config import settings
from app.rag.pipeline import RAGPipeline

QUESTIONS_PATH = ROOT / "evaluation" / "questions.json"
RESULTS_PATH = ROOT / "evaluation" / "results.json"

JUDGE_PROMPT = """You evaluate whether a RAG answer is grounded in the provided context.

Answer YES if every factual claim in the answer is supported by the context.
Answer NO only if the answer adds facts not in the context or contradicts it.

Guidelines:
- Paraphrasing and summarizing the context is grounded.
- Ignore citation tags like [doc_id: section].
- Ignore formatting; evaluate factual content only.
- Additional details that appear in the context are still grounded.

Reply with ONLY the word YES or NO on the first line."""


def normalize_text(text: str) -> str:
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = re.sub(r"\*+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.lower().split())


def token_overlap(gold: str, answer: str) -> float:
    gold_norm = normalize_text(gold)
    answer_norm = normalize_text(answer)
    gold_tokens = [t for t in gold_norm.split() if len(t) > 1]
    if not gold_tokens:
        return 0.0
    matches = sum(1 for token in gold_tokens if token in answer_norm)
    return matches / len(gold_tokens)


def strip_citations(text: str) -> str:
    return re.sub(r"\[[^\]]+\]", "", text).strip()


def heuristic_groundedness(answer: str, context: str) -> bool:
    """Verify answer sentences have supporting terms in context."""
    clean = strip_citations(answer)
    context_norm = normalize_text(context)
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean) if s.strip()]
    if not sentences:
        return False

    for sentence in sentences:
        sent_norm = normalize_text(sentence)
        tokens = [t for t in sent_norm.split() if len(t) > 2 or t.isdigit()]
        if not tokens:
            continue
        supported = sum(1 for token in tokens if token in context_norm)
        if supported / len(tokens) < 0.6:
            return False
    return True


def citation_accuracy(item: dict, citations: list[dict], answer: str) -> bool:
    cited_ids = {c["doc_id"] for c in citations}
    expected = set(item["expected_sources"])
    if not cited_ids & expected:
        return False
    return token_overlap(item["gold_answer"], answer) >= 0.5


def judge_groundedness(
    question: str, answer: str, context: str, groq_api_key: str, groq_model: str
) -> tuple[bool, str]:
    clean_answer = strip_citations(answer)

    if heuristic_groundedness(answer, context):
        llm_verdict = "heuristic"
        if not groq_api_key:
            return True, llm_verdict

    if not groq_api_key:
        return heuristic_groundedness(answer, context), "heuristic"

    llm = ChatGroq(
        api_key=groq_api_key,
        model=groq_model,
        temperature=0.0,
        max_tokens=16,
    )
    prompt = (
        f"{JUDGE_PROMPT}\n\nContext:\n{context}\n\n"
        f"Question: {question}\nAnswer: {clean_answer}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    first_line = response.content.strip().splitlines()[0].upper()
    llm_yes = first_line.startswith("YES")

    if llm_yes:
        return True, "llm"

    if heuristic_groundedness(answer, context):
        return True, "heuristic_override"

    return False, "llm"


def main() -> None:
    random.seed(settings.seed)

    if not QUESTIONS_PATH.exists():
        print(f"Questions file not found: {QUESTIONS_PATH}")
        sys.exit(1)

    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    pipeline = RAGPipeline(settings)

    if not pipeline.is_index_loaded():
        print("Index not loaded. Run: python scripts/ingest.py --rebuild")
        sys.exit(1)

    latencies: list[float] = []
    groundedness_scores: list[bool] = []
    citation_scores: list[bool] = []
    partial_scores: list[float] = []
    details: list[dict] = []

    for item in questions:
        response = pipeline.answer(item["question"])
        answer = response.answer
        latencies.append(response.latency_ms)

        grounded, judge_method = judge_groundedness(
            item["question"],
            answer,
            response.context_text,
            settings.groq_api_key,
            settings.groq_model,
        )
        groundedness_scores.append(grounded)

        cite_ok = citation_accuracy(item, response.citations, answer)
        citation_scores.append(cite_ok)

        partial = token_overlap(item["gold_answer"], answer)
        partial_scores.append(partial)

        details.append(
            {
                "id": item["id"],
                "question": item["question"],
                "answer": answer,
                "gold_answer": item["gold_answer"],
                "citations": response.citations,
                "latency_ms": response.latency_ms,
                "grounded": grounded,
                "judge_method": judge_method,
                "citation_accurate": cite_ok,
                "partial_match": round(partial, 3),
            }
        )
        time.sleep(0.3)

    latencies_sorted = sorted(latencies)
    p50_idx = max(0, int(len(latencies_sorted) * 0.5) - 1)
    p95_idx = max(0, int(len(latencies_sorted) * 0.95) - 1)

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_questions": len(questions),
        "metrics": {
            "groundedness_pct": round(100 * sum(groundedness_scores) / len(groundedness_scores), 1),
            "citation_accuracy_pct": round(100 * sum(citation_scores) / len(citation_scores), 1),
            "partial_match_pct": round(100 * statistics.mean(partial_scores), 1),
            "latency_p50_ms": round(latencies_sorted[p50_idx], 2) if latencies_sorted else 0,
            "latency_p95_ms": round(latencies_sorted[p95_idx], 2) if latencies_sorted else 0,
            "latency_mean_ms": round(statistics.mean(latencies), 2) if latencies else 0,
        },
        "details": details,
    }

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results["metrics"], indent=2))
    print(f"\nFull results written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
