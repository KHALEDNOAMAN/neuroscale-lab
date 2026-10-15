"""Welch power spectral density and band-power features."""
from __future__ import annotations

import numpy as np
from scipy.signal import welch

BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
}


def welch_psd(
    signal: np.ndarray,
    sfreq: float,
    nperseg: int | None = None,
    noverlap: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return one-sided density-normalized Welch PSD.

    Detrending is constant per segment; the default Hann window and 50% overlap
    follow SciPy's established Welch implementation. ``nperseg`` defaults to the
    shorter of 2 seconds and the available signal. Frequency resolution is
    ``sfreq / nperseg`` before zero-padding (no zero-padding is used here).
    """
    x = np.asarray(signal, dtype=float).ravel()
    if x.size < 4 or not np.isfinite(x).all():
        raise ValueError("signal must contain at least four finite samples")
    if sfreq <= 0:
        raise ValueError("sfreq must be positive")
    segment = min(x.size, int(nperseg or round(2.0 * sfreq)))
    if segment < 4:
        raise ValueError("nperseg must be at least four samples")
    overlap = segment // 2 if noverlap is None else int(noverlap)
    if not 0 <= overlap < segment:
        raise ValueError("noverlap must satisfy 0 <= noverlap < nperseg")
    frequencies, power = welch(
        x,
        fs=sfreq,
        window="hann",
        nperseg=segment,
        noverlap=overlap,
        detrend="constant",
        scaling="density",
        return_onesided=True,
    )
    return frequencies, power


def bandpower(
    signal: np.ndarray,
    sfreq: float,
    band: tuple[float, float],
    nperseg: int | None = None,
) -> float:
    """Integrate Welch PSD over [low, high), using trapezoidal integration."""
    low, high = band
    if low < 0 or low >= high:
        raise ValueError("band must satisfy 0 <= low < high")
    frequencies, power = welch_psd(signal, sfreq, nperseg=nperseg)
    if low < frequencies[0] or high > frequencies[-1]:
        return float("nan")
    interior = frequencies[(frequencies > low) & (frequencies < high)]
    grid = np.concatenate(([low], interior, [high]))
    values = np.interp(grid, frequencies, power)
    return float(np.trapezoid(values, grid)) if grid.size >= 2 else float("nan")


def spectral_features(signal: np.ndarray, sfreq: float, nperseg: int | None = None) -> dict[str, float]:
    powers = {name: bandpower(signal, sfreq, limits, nperseg=nperseg) for name, limits in BANDS.items()}
    total = float(np.nansum(list(powers.values())))
    relative = {
        f"relative_{name}": value / total if total > 0 and np.isfinite(value) else float("nan")
        for name, value in powers.items()
    }
    return {**powers, **relative}
