import numpy as np

from neuroscale.features.entropy import multiscale_permutation_entropy, permutation_entropy


def test_constant_signal_has_zero_entropy():
    assert permutation_entropy(np.ones(100)) == 0.0

def test_entropy_is_bounded():
    rng = np.random.default_rng(1); h = permutation_entropy(rng.normal(size=10000), order=3)
    assert 0 <= h <= 1

def test_short_signal_nan_and_invalid_params():
    assert np.isnan(permutation_entropy(np.ones(2), order=3))
    try: permutation_entropy(np.ones(10), order=1)
    except ValueError: pass
    else: raise AssertionError("invalid order accepted")

def test_multiscale_keys():
    out = multiscale_permutation_entropy(np.arange(100.0), [1, 2, 4])
    assert set(out) == {1, 2, 4}
