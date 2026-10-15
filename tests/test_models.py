import numpy as np
import pandas as pd
import pytest

from neuroscale.models.evaluate import evaluate_grouped, make_logistic_pipeline


def synthetic_table() -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(5)
    for subject in range(6):
        for level in range(1, 5):
            for epoch in range(3):
                rows.extend([
                    {"subject_code": f"s{subject}", "epoch_index": (level - 1) * 3 + epoch, "workload_level": level, "feature_name": "alpha", "feature_value": float(level) + rng.normal(0, 0.1)},
                    {"subject_code": f"s{subject}", "epoch_index": (level - 1) * 3 + epoch, "workload_level": level, "feature_name": "permutation_entropy", "feature_value": float(level) / 4 + rng.normal(0, 0.03)},
                ])
    return pd.DataFrame(rows)


def test_grouped_evaluation_never_reuses_test_subjects():
    results = evaluate_grouped(synthetic_table(), n_splits=3)
    for result in results:
        assert len(result.test_subjects) == len(set(result.test_subjects))
        assert result.balanced_accuracy >= 0
        assert result.macro_f1 >= 0


def test_grouped_evaluation_requires_multiple_participants():
    table = synthetic_table().query("subject_code == 's0'")
    with pytest.raises(ValueError, match="three participants"):
        evaluate_grouped(table)


def test_heldout_values_do_not_change_training_imputation_or_scaling():
    x_train = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [10.0, 20.0, 30.0]})
    x_test = pd.DataFrame({"a": [np.nan], "b": [100.0]})
    first = make_logistic_pipeline().fit(x_train, [1, 2, 3])
    altered = make_logistic_pipeline().fit(x_train, [1, 2, 3])
    first_imputer = first.named_steps["simpleimputer"]
    altered_imputer = altered.named_steps["simpleimputer"]
    assert np.array_equal(first_imputer.statistics_, altered_imputer.statistics_)
    assert np.array_equal(first.named_steps["standardscaler"].mean_, altered.named_steps["standardscaler"].mean_)
    assert not np.isnan(first.predict(x_test)).any()
