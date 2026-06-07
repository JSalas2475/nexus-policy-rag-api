import hashlib
import re
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    chunk_id: str
    content: str
    metadata: dict


def chunk_documents(sections: list[dict], seed: int = 42) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for section in sections:
        content = section["content"]
        pieces = _split_text(content, chunk_size=512, overlap=64)

        for idx, piece in enumerate(pieces):
            metadata = {
                "doc_id": section["doc_id"],
                "title": section["title"],
                "section": section["section"],
                "source_path": section["source_path"],
                "page_or_heading": section["page_or_heading"],
                "chunk_index": idx,
            }
            chunk_id = _make_chunk_id(metadata, piece)
            chunks.append(DocumentChunk(chunk_id=chunk_id, content=piece, metadata=metadata))

    chunks.sort(key=lambda chunk: chunk.chunk_id)
    return chunks


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            split_at = _find_split_point(text, start, end, chunk_size)
            if split_at > start:
                end = split_at
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return pieces


def _find_split_point(text: str, start: int, end: int, chunk_size: int) -> int:
    window = text[start:end]
    for separator in ["\n\n", "\n", ". ", " "]:
        idx = window.rfind(separator)
        if idx > chunk_size // 3:
            return start + idx + len(separator)
    return end


def _make_chunk_id(metadata: dict, content: str) -> str:
    raw = f"{metadata['doc_id']}:{metadata['section']}:{metadata['chunk_index']}:{content[:80]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
