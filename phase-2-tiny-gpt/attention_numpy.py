"""Attention two ways — the vectorization (SIMD) lesson of Phase 2.

You implement the same math twice: once with explicit Python loops (``attention_naive``)
and once with vectorized NumPy matrix ops (``attention_vectorized``). They must return the
same result; in the Colab notebook you time both and see the speedup that vectorization
(and, under the hood, SIMD/AVX) buys you.

Pure NumPy — no torch — so the autograder runs it fast. Run the unit tests as you go:

    python -m pytest phase-2-tiny-gpt/tests/test_units.py -p autograder.points -q
"""

from __future__ import annotations

import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax along ``axis`` (provided)."""
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


def attention_naive(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Scaled dot-product attention with **explicit loops** over positions.

    Q, K, V each have shape ``(T, d)``. Return shape ``(T, d)``:
        scores[i,j] = (Q[i] . K[j]) / sqrt(d);  weights = softmax(scores, axis=-1);
        out[i] = sum_j weights[i,j] * V[j]
    Loop over the query index ``i`` and key index ``j`` — do NOT use ``Q @ K.T``.
    """
    T, d = Q.shape
    scores = np.zeros((T, T), dtype=Q.dtype)

    for i in range(T):
        for j in range(T):
            dot_product = 0.0
            for k in range(d):
                dot_product += Q[i, k] * K[j, k]
            scores[i, j] = dot_product / np.sqrt(d)
    
    weights = softmax(scores, axis=-1)

    out = np.zeros((T, d), dtype=Q.dtype)
    for i in range(T):
        for j in range(T):
            for k in range(d):
                out[i, k] += weights[i, j] * V[j, k]
    return out
    raise NotImplementedError("Phase 2: implement attention_naive()")


def attention_vectorized(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
    """The same attention using vectorized matrix ops — no Python loops over positions."""
    d = Q.shape[1]
    
    scores = (Q @ K.T) / np.sqrt(d)
    
    weights = softmax(scores, axis=-1)
    
    return weights @ V
    raise NotImplementedError("Phase 2: implement attention_vectorized()")
