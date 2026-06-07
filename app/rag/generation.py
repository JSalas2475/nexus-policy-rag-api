import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.rag.retrieval import RetrievedChunk

SYSTEM_PROMPT = """You are a policy assistant for Nexus Technologies.
Rules:
- Answer ONLY using the provided policy context.
- If the question is outside company policies, respond exactly: "I can only answer about our company policies."
- Use plain text only (no markdown, no bullet lists).
- Answer in 1-2 concise sentences. State the direct answer first.
- Always end with one citation in the format [doc_id: section].
- Do not invent policies, numbers, or procedures not present in the context.
- Do not add information beyond what is needed to answer the question.
"""

REFUSAL_MESSAGE = "I can only answer about our company policies."


def format_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for chunk in chunks:
        blocks.append(
            f"[Source: {chunk.doc_id} | Section: {chunk.section}]\n{chunk.content}"
        )
    return "\n\n---\n\n".join(blocks)


def generate_answer(
    question: str,
    chunks: list[RetrievedChunk],
    groq_api_key: str,
    groq_model: str,
    max_answer_words: int,
) -> str:
    if not groq_api_key:
        return _fallback_answer(question, chunks, max_answer_words)

    llm = ChatGroq(
        api_key=groq_api_key,
        model=groq_model,
        temperature=0.1,
        max_tokens=512,
    )

    context = format_context(chunks)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer with citations:"
        ),
    ]

    response = llm.invoke(messages)
    answer = response.content.strip()
    return truncate_words(answer, max_answer_words)


def _fallback_answer(
    question: str, chunks: list[RetrievedChunk], max_answer_words: int
) -> str:
    if not chunks:
        return REFUSAL_MESSAGE
    top = chunks[0]
    answer = (
        f"Based on {top.doc_id} ({top.section}): {top.content[:400]} "
        f"[{top.doc_id}: {top.section}]"
    )
    return truncate_words(answer, max_answer_words)


def truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def extract_citations(answer: str, chunks: list[RetrievedChunk]) -> list[dict]:
    pattern = re.compile(r"\[([^\]:]+):\s*([^\]]+)\]")
    chunk_map = {(chunk.doc_id, chunk.section): chunk for chunk in chunks}
    doc_map = {chunk.doc_id: chunk for chunk in chunks}

    citations: list[dict] = []
    seen: set[str] = set()

    for match in pattern.finditer(answer):
        doc_id = match.group(1).strip()
        section = match.group(2).strip()
        key = f"{doc_id}:{section}"
        if key in seen:
            continue
        seen.add(key)

        chunk = chunk_map.get((doc_id, section)) or doc_map.get(doc_id)
        if chunk:
            citations.append(
                {
                    "doc_id": chunk.doc_id,
                    "title": chunk.title,
                    "section": chunk.section,
                    "snippet": chunk.snippet,
                    "source_path": chunk.source_path,
                }
            )

    if not citations and chunks:
        chunk = chunks[0]
        citations.append(
            {
                "doc_id": chunk.doc_id,
                "title": chunk.title,
                "section": chunk.section,
                "snippet": chunk.snippet,
                "source_path": chunk.source_path,
            }
        )

    return citations
