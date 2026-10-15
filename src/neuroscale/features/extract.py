from __future__ import annotations

import numpy as np

from .entropy import multiscale_permutation_entropy, permutation_entropy
from .spectral import spectral_features


def extract_features(
    signal: np.ndarray,
    sfreq: float,
    scales: list[int] | None = None,
    nperseg: int | None = None,
) -> dict[str, float]:
    scales = [2, 4, 8] if scales is None else [int(scale) for scale in scales if int(scale) > 1]
    result = spectral_features(signal, sfreq, nperseg=nperseg)
    result["permutation_entropy"] = permutation_entropy(signal)
    result.update({f"mpe_scale_{scale}": value for scale, value in multiscale_permutation_entropy(signal, scales).items()})
    return result
