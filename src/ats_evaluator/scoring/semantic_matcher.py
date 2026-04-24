"""Semantic skill matching using sentence-transformers (optional dependency).

If sentence-transformers is not installed, all public functions degrade gracefully:
- is_available() returns False
- semantic_similarity() returns 0.0
- semantic_skills_overlap() returns empty set
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy import ndarray

# ---------------------------------------------------------------------------
# Optional import — graceful degradation if not installed
# ---------------------------------------------------------------------------

try:
    from sentence_transformers import SentenceTransformer as _SentenceTransformer

    _LIBRARY_AVAILABLE = True
except ImportError:
    _LIBRARY_AVAILABLE = False

_MODEL_NAME = "all-MiniLM-L6-v2"
_MODEL: "_SentenceTransformer | None" = None
_MODEL_LOAD_FAILED = False

_EMBEDDING_CACHE: dict[str, list[float]] = {}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_model() -> "_SentenceTransformer | None":
    """Lazy-load the embedding model on first use."""
    global _MODEL, _MODEL_LOAD_FAILED  # noqa: PLW0603

    if _MODEL_LOAD_FAILED or not _LIBRARY_AVAILABLE:
        return None
    if _MODEL is not None:
        return _MODEL

    try:
        _MODEL = _SentenceTransformer(_MODEL_NAME)
    except Exception as exc:  # noqa: BLE001
        print(
            f"[semantic_matcher] WARNING: failed to load model '{_MODEL_NAME}': {exc}",
            file=sys.stderr,
        )
        _MODEL_LOAD_FAILED = True
        return None

    return _MODEL


def _embed(text: str) -> "ndarray | None":
    """Return embedding for *text*, using the module-level cache."""
    model = _load_model()
    if model is None:
        return None

    import numpy as np  # sentence-transformers always pulls numpy

    if text not in _EMBEDDING_CACHE:
        vec = model.encode(text, batch_size=1)
        _EMBEDDING_CACHE[text] = vec.tolist()

    return np.array(_EMBEDDING_CACHE[text], dtype=float)


def _embed_batch(texts: list[str]) -> "list[ndarray] | None":
    """Encode a batch of texts, reusing cache entries where possible."""
    model = _load_model()
    if model is None:
        return None

    import numpy as np

    uncached = [t for t in texts if t not in _EMBEDDING_CACHE]
    if uncached:
        vecs = model.encode(uncached, batch_size=32)
        for text, vec in zip(uncached, vecs):
            _EMBEDDING_CACHE[text] = vec.tolist()

    return [np.array(_EMBEDDING_CACHE[t], dtype=float) for t in texts]


def _cosine(a: "ndarray", b: "ndarray") -> float:
    """Cosine similarity between two 1-D vectors."""
    import numpy as np

    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_available() -> bool:
    """Return True if sentence-transformers is installed and the model loads."""
    return _load_model() is not None


def semantic_similarity(text_a: str, text_b: str) -> float:
    """Cosine similarity between two texts. Returns 0.0 if not available."""
    vec_a = _embed(text_a)
    vec_b = _embed(text_b)
    if vec_a is None or vec_b is None:
        return 0.0
    return _cosine(vec_a, vec_b)


def semantic_skills_overlap(
    cv_skills: tuple[str, ...],
    jd_skills: tuple[str, ...],
    threshold: float = 0.72,
) -> set[str]:
    """Return JD skills that have a semantic match in cv_skills above threshold.

    Each JD skill is compared against every CV skill; the maximum similarity
    determines whether the JD skill is considered matched. The canonical JD
    skill name is used as the key in the returned set.

    Returns an empty set when sentence-transformers is not available.
    """
    if not cv_skills or not jd_skills:
        return set()

    model = _load_model()
    if model is None:
        return set()

    all_texts = list(cv_skills) + list(jd_skills)
    embeddings = _embed_batch(all_texts)
    if embeddings is None:
        return set()

    cv_vecs = embeddings[: len(cv_skills)]
    jd_vecs = embeddings[len(cv_skills) :]

    matched: set[str] = set()
    for jd_skill, jd_vec in zip(jd_skills, jd_vecs):
        max_sim = max(_cosine(jd_vec, cv_vec) for cv_vec in cv_vecs)
        if max_sim >= threshold:
            matched.add(jd_skill)

    return matched
