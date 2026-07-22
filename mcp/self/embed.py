"""Embedding wrapper (fastembed, local, keyless) + cosine search."""
from __future__ import annotations

import numpy as np
from config import EMBED_MODEL  # noqa

_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        from fastembed import TextEmbedding
        _MODEL = TextEmbedding(model_name=EMBED_MODEL)
    return _MODEL


def embed(text: str) -> list[float]:
    if not text or not text.strip():
        text = " "
    v = list(_model().embed([text]))[0]
    return v.astype(np.float32).tolist()


def cosine(a: list[float], b: list[float]) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))
