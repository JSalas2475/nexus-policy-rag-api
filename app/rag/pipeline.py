import time
from dataclasses import dataclass

from app.config import Settings
from app.rag.generation import format_context, generate_answer
from app.rag.guardrails import apply_guardrails
from app.rag.retrieval import Retriever
from app.rag.vectorstore import VectorStoreManager


@dataclass
class RAGResponse:
    answer: str
    citations: list[dict]
    latency_ms: float
    refused: bool
    retrieved_chunks: list[dict]
    context_text: str


class RAGPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.vectorstore_manager = VectorStoreManager(
            persist_dir=settings.chroma_persist_dir,
            embedding_model_name=settings.embedding_model,
        )
        self.retriever = Retriever(
            vectorstore_manager=self.vectorstore_manager,
            retrieval_k=settings.retrieval_k,
            rerank_k=settings.rerank_k,
            rerank_model=settings.rerank_model,
        )

    def is_index_loaded(self) -> bool:
        return self.vectorstore_manager.is_loaded()

    def answer(self, question: str) -> RAGResponse:
        start = time.perf_counter()
        chunks = self.retriever.retrieve(question)

        raw_answer = generate_answer(
            question=question,
            chunks=chunks,
            groq_api_key=self.settings.groq_api_key,
            groq_model=self.settings.groq_model,
            max_answer_words=self.settings.max_answer_words,
        )

        answer, citations, refused = apply_guardrails(
            question=question,
            chunks=chunks,
            raw_answer=raw_answer,
            score_threshold=self.settings.retrieval_score_threshold,
            max_answer_words=self.settings.max_answer_words,
        )

        latency_ms = (time.perf_counter() - start) * 1000
        return RAGResponse(
            answer=answer,
            citations=citations,
            latency_ms=round(latency_ms, 2),
            refused=refused,
            retrieved_chunks=[
                {
                    "doc_id": chunk.doc_id,
                    "section": chunk.section,
                    "score": chunk.score,
                    "snippet": chunk.snippet,
                    "content": chunk.content,
                }
                for chunk in chunks
            ],
            context_text=format_context(chunks),
        )
