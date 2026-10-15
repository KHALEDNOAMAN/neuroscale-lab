import numpy as np

from neuroscale.ingestion.qc import classify_event


def test_qc_handles_nan_labels_and_tutorials():
    decision = classify_event({"nback_level": np.nan, "trial_type": "dropped_samples", "onset": 1.0}, [], 1.0)
    assert not decision.include
    tutorial = classify_event({"nback_level": 1, "trial_type": "1-back", "istutorial": "True", "onset": 1.0}, [], 1.0)
    assert tutorial.reason == "tutorial_event"


def test_qc_rejects_dropout_overlap_and_accepts_clean_event():
    excluded = classify_event({"nback_level": 2, "trial_type": "2-back", "onset": 1.0}, [1.5], 1.0)
    assert excluded.reason == "dropout_overlap"
    included = classify_event({"nback_level": 2, "trial_type": "2-back", "onset": 1.0}, [2.1], 1.0)
    assert included.include


def test_qc_checks_sample_boundaries_with_same_rounding_as_extraction():
    event = {"nback_level": 3, "trial_type": "3-back", "onset": 1076.884421}
    # With 250 Hz, this 1-second epoch falls beyond the final sample.
    decision = classify_event(
        event, [], 1.0, sampling_frequency=250.0, recording_samples=269376
    )
    assert not decision.include
    assert decision.reason == "boundary_invalid"
    assert classify_event(
        {**event, "onset": 1075.0}, [], 1.0,
        sampling_frequency=250.0, recording_samples=269376,
    ).include


def test_qc_requires_both_boundary_parameters():
    import pytest

    with pytest.raises(ValueError, match="passed together"):
        classify_event(
            {"nback_level": 1, "trial_type": "1-back", "onset": 1.0},
            [], 1.0, sampling_frequency=250.0,
        )
