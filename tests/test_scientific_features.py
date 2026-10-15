import numpy as np
import pytest

from neuroscale.features.entropy import permutation_entropy
from neuroscale.features.extract import extract_features
from neuroscale.features.spectral import bandpower, welch_psd


def test_entropy_rejects_nonfinite_inputs():
    with pytest.raises(ValueError, match="NaN"):
        permutation_entropy(np.array([0.0, 1.0, np.nan, 2.0, 3.0, 4.0]))


def test_entropy_rejects_multidimensional_inputs():
    with pytest.raises(ValueError, match="one-dimensional"):
        permutation_entropy(np.ones((2, 10)))


def test_monotone_signal_has_zero_entropy():
    assert permutation_entropy(np.arange(100.0)) == 0.0


def test_welch_peak_and_frequency_resolution():
    sfreq = 250.0
    t = np.arange(0, 8, 1 / sfreq)
    signal = np.sin(2 * np.pi * 10 * t)
    frequencies, power = welch_psd(signal, sfreq, nperseg=500)
    peak = frequencies[np.argmax(power)]
    assert abs(peak - 10.0) <= sfreq / 500


def test_sinusoid_bandpower_is_concentrated_in_alpha():
    sfreq = 250.0
    t = np.arange(0, 8, 1 / sfreq)
    signal = np.sin(2 * np.pi * 10 * t)
    alpha = bandpower(signal, sfreq, (8, 13), nperseg=500)
    beta = bandpower(signal, sfreq, (13, 30), nperseg=500)
    assert alpha > 10 * beta


def test_scale_one_is_not_duplicated():
    names = extract_features(np.random.default_rng(3).normal(size=1000), 250).keys()
    assert "mpe_scale_1" not in names
    assert "permutation_entropy" in names
