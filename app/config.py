import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    groq_model: str
    embedding_model: str
    rerank_model: str
    chroma_persist_dir: Path
    policies_dir: Path
    retrieval_k: int
    rerank_k: int
    retrieval_score_threshold: float
    max_answer_words: int
    seed: int
    flask_env: str
    flask_debug: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
            rerank_model=os.getenv(
                "RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
            ),
            chroma_persist_dir=Path(
                os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))
            ),
            policies_dir=Path(os.getenv("POLICIES_DIR", str(BASE_DIR / "data" / "policies"))),
            retrieval_k=int(os.getenv("RETRIEVAL_K", "10")),
            rerank_k=int(os.getenv("RERANK_K", "4")),
            retrieval_score_threshold=float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.35")),
            max_answer_words=int(os.getenv("MAX_ANSWER_WORDS", "300")),
            seed=int(os.getenv("SEED", "42")),
            flask_env=os.getenv("FLASK_ENV", "development"),
            flask_debug=os.getenv("FLASK_DEBUG", "0") == "1",
        )


settings = Settings.from_env()
