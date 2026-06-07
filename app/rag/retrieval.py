from dataclasses import dataclass
from functools import lru_cache


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    doc_id: str
    title: str
    section: str
    source_path: str
    snippet: str
    score: float
    similarity_score: float


@lru_cache(maxsize=1)
def get_reranker(model_name: str):
    try:
        from sentence_transformers import CrossEncoder

        return CrossEncoder(model_name)
    except (ImportError, OSError):
        return None


class Retriever:
    def __init__(
        self,
        vectorstore_manager,
        retrieval_k: int,
        rerank_k: int,
        rerank_model: str,
    ):
        self.vectorstore_manager = vectorstore_manager
        self.retrieval_k = retrieval_k
        self.rerank_k = rerank_k
        self.rerank_model = rerank_model

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        vectorstore = self.vectorstore_manager.get_vectorstore()
        if vectorstore is None:
            return []

        results = vectorstore.similarity_search_with_relevance_scores(
            query, k=self.retrieval_k
        )
        if not results:
            return []

        candidates: list[RetrievedChunk] = []
        for doc, score in results:
            metadata = doc.metadata
            content = doc.page_content
            candidates.append(
                RetrievedChunk(
                    chunk_id=metadata.get("chunk_id", metadata.get("doc_id", "unknown")),
                    content=content,
                    doc_id=metadata.get("doc_id", "unknown"),
                    title=metadata.get("title", metadata.get("doc_id", "unknown")),
                    section=metadata.get("section", "unknown"),
                    source_path=metadata.get("source_path", ""),
                    snippet=content[:200] + ("..." if len(content) > 200 else ""),
                    score=float(score),
                    similarity_score=float(score),
                )
            )

        if len(candidates) <= self.rerank_k:
            return candidates

        reranker = get_reranker(self.rerank_model)
        if reranker is None:
            return sorted(candidates, key=lambda c: c.similarity_score, reverse=True)[
                : self.rerank_k
            ]

        pairs = [[query, chunk.content] for chunk in candidates]
        rerank_scores = reranker.predict(pairs)

        scored = sorted(
            zip(candidates, rerank_scores, strict=True),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        reranked: list[RetrievedChunk] = []
        for chunk, rerank_score in scored[: self.rerank_k]:
            reranked.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    doc_id=chunk.doc_id,
                    title=chunk.title,
                    section=chunk.section,
                    source_path=chunk.source_path,
                    snippet=chunk.snippet,
                    score=float(rerank_score),
                    similarity_score=chunk.similarity_score,
                )
            )
        return reranked
