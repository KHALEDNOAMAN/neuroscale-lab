from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class FoldResult:
    feature_group: str
    model_name: str
    fold_id: int
    test_subjects: tuple[str, ...]
    balanced_accuracy: float
    macro_f1: float
    confusion_matrix: str


def pivot_features(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    required = {"subject_code", "epoch_index", "workload_level", "feature_name", "feature_value"}
    missing = required.difference(table.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    wide = table.pivot_table(
        index=["subject_code", "epoch_index", "workload_level"],
        columns="feature_name",
        values="feature_value",
        aggfunc="first",
    ).reset_index()
    groups = wide.pop("subject_code")
    y = wide.pop("workload_level")
    return wide.drop(columns=["epoch_index"]), y, groups


def _record(
    feature_group: str,
    model_name: str,
    fold_id: int,
    groups: pd.Series,
    y_true: pd.Series,
    prediction: np.ndarray,
) -> FoldResult:
    labels = sorted(y_true.unique())
    matrix = confusion_matrix(y_true, prediction, labels=labels)
    return FoldResult(
        feature_group,
        model_name,
        fold_id,
        tuple(sorted(set(groups))),
        float(balanced_accuracy_score(y_true, prediction)),
        float(f1_score(y_true, prediction, average="macro", zero_division=0)),
        json.dumps(matrix.tolist()),
    )


def make_logistic_pipeline():
    """Return the fixed logistic model with imputation and scaling in-pipeline."""
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=2000, C=1.0),
    )


def select_feature_sets(columns: Iterable[str]) -> dict[str, list[str]]:
    """Select feature groups from plain and channel-prefixed feature names.

    Full-cohort names are like 'Fp1__mpe_scale_2', not 'mpe_scale_2'.
    Preserve the existing spectral selection policy; fix the entropy selection.
    """
    names = list(columns)
    return {
        "spectral": [
            c for c in names
            if any(token in c for token in ("delta", "theta", "alpha", "beta"))
        ],
        "entropy": [
            c for c in names
            if "entropy" in c.rsplit("__", 1)[-1]
            or c.rsplit("__", 1)[-1].startswith("mpe_scale_")
        ],
        "combined": names,
    }


def evaluate_grouped(table: pd.DataFrame, n_splits: int = 5) -> list[FoldResult]:
    """Evaluate fixed models with participant-grouped folds.

    Imputation and scaling are pipeline steps, so their fitted statistics are
    computed on each training fold only. The returned folds never share a
    participant between training and evaluation partitions.
    """
    x, y, groups = pivot_features(table)
    unique_groups = np.unique(groups)
    if len(unique_groups) < 3:
        raise ValueError("at least three participants are required for grouped evaluation")
    n_splits = min(n_splits, len(unique_groups))
    feature_sets = select_feature_sets(x.columns)
    models = {
        "logistic_regression": make_logistic_pipeline(),
        "hist_gradient_boosting": make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(max_iter=100, learning_rate=0.08, random_state=20261014),
        ),
    }
    results: list[FoldResult] = []
    splitter = GroupKFold(n_splits=n_splits)
    for feature_group, columns in feature_sets.items():
        if not columns:
            continue
        data = x[columns].replace([np.inf, -np.inf], np.nan)
        splits = list(splitter.split(data, y, groups))
        for model_name, model in models.items():
            for fold_id, (train, test) in enumerate(splits):
                train_subjects = set(groups.iloc[train])
                test_subjects = set(groups.iloc[test])
                assert train_subjects.isdisjoint(test_subjects), "participant leakage between train and test folds"
                fitted = clone(model).fit(data.iloc[train], y.iloc[train])
                prediction = fitted.predict(data.iloc[test])
                results.append(_record(feature_group, model_name, fold_id, groups.iloc[test], y.iloc[test], prediction))
        for fold_id, (train, test) in enumerate(splits):
            train_subjects = set(groups.iloc[train])
            test_subjects = set(groups.iloc[test])
            assert train_subjects.isdisjoint(test_subjects), "participant leakage between train and test folds"
            majority = y.iloc[train].mode().iloc[0]
            prediction = np.full(len(test), majority)
            results.append(_record(feature_group, "majority_baseline", fold_id, groups.iloc[test], y.iloc[test], prediction))
    return results
