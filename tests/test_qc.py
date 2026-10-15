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
