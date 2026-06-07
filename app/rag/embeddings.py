import logging
import os
from functools import lru_cache

import requests
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_API_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class FastEmbedEmbeddings(Embeddings):
    """ONNX-based local embeddings (Linux/Render; needs VC++ on Windows)."""

    def __init__(self, model_name: str):
        from fastembed import TextEmbedding

        self.model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vec.tolist() for vec in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(self.model.embed([text])).tolist()


class HuggingFaceAPIEmbeddings(Embeddings):
    """Remote embeddings via HuggingFace Inference API (no local DLLs)."""

    def __init__(self, model_name: str, api_token: str):
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": text, "options": {"wait_for_model": True}},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and data and isinstance(data[0], list):
            if data and isinstance(data[0][0], (int, float)):
                return [float(x) for x in data[0]]
            token_vectors = data[0]
            dim = len(token_vectors[0])
            pooled = [0.0] * dim
            for vec in token_vectors:
                for i, val in enumerate(vec):
                    pooled[i] += float(val)
            return [v / len(token_vectors) for v in pooled]
        raise ValueError(f"Unexpected HF API response format for {self.model_name}")


def _resolve_hf_token() -> str:
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or ""


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str) -> Embeddings:
    backend = os.getenv("EMBEDDING_BACKEND", "auto").lower()

    if backend in ("auto", "local"):
        local_model = model_name if "bge" in model_name.lower() else DEFAULT_LOCAL_MODEL
        try:
            return FastEmbedEmbeddings(local_model)
        except Exception as exc:
            if backend == "local":
                raise RuntimeError(
                    "Local embeddings failed. On Windows, install VC++ Redistributable: "
                    "https://aka.ms/vs/17/release/vc_redist.x64.exe"
                ) from exc
            logger.warning("Local embeddings unavailable (%s), trying HF API...", exc)

    token = _resolve_hf_token()
    if not token:
        raise RuntimeError(
            "Embeddings failed. Fix one of:\n"
            "  1) Install VC++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
            "  2) Set HF_TOKEN in .env and EMBEDDING_BACKEND=api (free: huggingface.co/settings/tokens)"
        )

    api_model = DEFAULT_API_MODEL
    if "bge" not in model_name.lower() and "sentence-transformers" in model_name:
        api_model = model_name

    return HuggingFaceAPIEmbeddings(api_model, token)
