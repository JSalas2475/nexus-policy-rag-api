#!/usr/bin/env python3
"""Build the Chroma vector index from policy documents."""

import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app.config import Settings
from app.rag.chunking import chunk_documents
from app.rag.ingestion import load_all_documents
from app.rag.vectorstore import VectorStoreManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest policy documents into Chroma.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild index from scratch")
    args = parser.parse_args()

    settings = Settings.from_env()
    random.seed(args.seed)

    policies_dir = settings.policies_dir
    if not policies_dir.exists():
        print(f"Policies directory not found: {policies_dir}")
        sys.exit(1)

    print(f"Loading documents from {policies_dir}...")
    sections = load_all_documents(policies_dir)
    print(f"Loaded {len(sections)} sections from policy files.")

    chunks = chunk_documents(sections, seed=args.seed)
    print(f"Created {len(chunks)} chunks.")

    manager = VectorStoreManager(
        persist_dir=settings.chroma_persist_dir,
        embedding_model_name=settings.embedding_model,
    )
    count = manager.build_index(chunks, rebuild=args.rebuild)
    print(f"Indexed {count} chunks into {settings.chroma_persist_dir}.")


if __name__ == "__main__":
    main()
