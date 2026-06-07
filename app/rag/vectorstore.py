from pathlib import Path

import chromadb
from langchain_community.vectorstores import Chroma

from app.rag.chunking import DocumentChunk
from app.rag.embeddings import get_embedding_model


class VectorStoreManager:
    COLLECTION_NAME = "policy_documents"

    def __init__(self, persist_dir: Path, embedding_model_name: str):
        self.persist_dir = persist_dir
        self.embedding_model_name = embedding_model_name
        self._embeddings = None
        self._vectorstore: Chroma | None = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = get_embedding_model(self.embedding_model_name)
        return self._embeddings

    def build_index(self, chunks: list[DocumentChunk], rebuild: bool = False) -> int:
        if rebuild and self.persist_dir.exists():
            import shutil

            shutil.rmtree(self.persist_dir)

        self.persist_dir.mkdir(parents=True, exist_ok=True)
        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]

        self._vectorstore = Chroma.from_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            embedding=self.embeddings,
            collection_name=self.COLLECTION_NAME,
            persist_directory=str(self.persist_dir),
        )
        return len(chunks)

    def load(self) -> bool:
        if not self.persist_dir.exists():
            return False

        try:
            client = chromadb.PersistentClient(path=str(self.persist_dir))
            collection = client.get_collection(self.COLLECTION_NAME)
            if collection.count() == 0:
                return False
        except Exception:
            return False

        try:
            self._vectorstore = Chroma(
                collection_name=self.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_dir),
            )
            return True
        except Exception:
            return False

    def get_vectorstore(self) -> Chroma | None:
        if self._vectorstore is None:
            self.load()
        return self._vectorstore

    def is_loaded(self) -> bool:
        if not self.persist_dir.exists():
            return False
        try:
            client = chromadb.PersistentClient(path=str(self.persist_dir))
            collection = client.get_collection(self.COLLECTION_NAME)
            return collection.count() > 0
        except Exception:
            return False
