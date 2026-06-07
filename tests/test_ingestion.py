import pytest

from app.rag.chunking import chunk_documents
from app.rag.ingestion import load_all_documents
from app.config import settings


def test_corpus_has_minimum_documents():
    files = list(settings.policies_dir.glob("*"))
    assert len(files) >= 10


def test_all_documents_have_required_metadata():
    sections = load_all_documents(settings.policies_dir)
    for section in sections:
        assert section["doc_id"]
        assert section["title"]
        assert section["source_path"]
        assert section["content"]


def test_chunk_ids_are_unique():
    sections = load_all_documents(settings.policies_dir)
    chunks = chunk_documents(sections, seed=42)
    ids = [chunk.chunk_id for chunk in chunks]
    assert len(ids) == len(set(ids))


def test_chunking_is_deterministic():
    sections = load_all_documents(settings.policies_dir)
    chunks_a = chunk_documents(sections, seed=42)
    chunks_b = chunk_documents(sections, seed=42)
    assert [c.chunk_id for c in chunks_a] == [c.chunk_id for c in chunks_b]
