"""Embedding engine using fastembed (local, no API needed)."""
from __future__ import annotations

import numpy as np
from functools import lru_cache
from typing import List

from config import EMBED_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(model_name=EMBED_MODEL)
    return _model


def embed(text: str) -> List[float]:
    """Embed a single text string → 384-dim vector."""
    model = _get_model()
    vecs = list(model.embed([text]))
    return vecs[0].tolist()


def embed_batch(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    """Embed multiple texts → list of 384-dim vectors."""
    if not texts:
        return []
    model = _get_model()
    vecs = list(model.embed(texts, batch_size=batch_size))
    return [v.tolist() for v in vecs]


def cosine(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    dot = float(np.dot(va, vb))
    na = float(np.linalg.norm(va))
    nb = float(np.linalg.norm(vb))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return dot / (na * nb)
