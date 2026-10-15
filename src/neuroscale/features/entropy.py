"""Ordinal-pattern entropy estimators with explicit finite-sample policies."""
from __future__ import annotations

import math

import numpy as np


def permutation_entropy(
    signal: np.ndarray,
    order: int = 3,
    delay: int = 1,
    normalize: bool = True,
    min_patterns: int | None = None,
) -> float:
    """Compute normalized Bandt--Pompe permutation entropy.

    Ties are resolved by stable sorting, which is deterministic but not tie-invariant.
    Non-finite observations raise ``ValueError`` because silently dropping samples
    changes ordinal-vector adjacency. By default at least ``m!`` ordinal vectors are
    required, so every possible pattern can in principle be observed.
    """
    array = np.asarray(signal, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError("signal must be a non-empty one-dimensional array")
    x = array
    if not np.isfinite(x).all():
        raise ValueError("signal contains NaN or infinite values")
    if order < 2 or delay < 1:
        raise ValueError("order must be >=2 and delay must be >=1")
    n_vectors = x.size - delay * (order - 1)
    required = math.factorial(order) if min_patterns is None else int(min_patterns)
    if required < 1:
        raise ValueError("min_patterns must be positive")
    if n_vectors < required:
        return float("nan")

    patterns = np.empty(n_vectors, dtype=np.int64)
    for i in range(n_vectors):
        ordinal = np.argsort(x[i : i + delay * order : delay], kind="stable")
        patterns[i] = np.ravel_multi_index(tuple(ordinal), (order,) * order)
    _, counts = np.unique(patterns, return_counts=True)
    probabilities = counts.astype(float) / n_vectors
    entropy = float(-np.sum(probabilities * np.log(probabilities)))
    return entropy / math.log(math.factorial(order)) if normalize else entropy


def multiscale_permutation_entropy(
    signal: np.ndarray,
    scales: list[int],
    order: int = 3,
    delay: int = 1,
) -> dict[int, float]:
    """Coarse-grain by non-overlapping means and calculate entropy per scale."""
    array = np.asarray(signal, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError("signal must be a non-empty one-dimensional array")
    x = array
    if not np.isfinite(x).all():
        raise ValueError("signal must be non-empty and finite")
    out: dict[int, float] = {}
    for scale in scales:
        if scale < 1:
            raise ValueError("scales must be positive")
        n = x.size // scale
        coarse = x[: n * scale].reshape(n, scale).mean(axis=1) if n else np.array([])
        out[int(scale)] = permutation_entropy(coarse, order=order, delay=delay)
    return out
