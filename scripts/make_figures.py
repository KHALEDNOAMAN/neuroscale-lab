"""Generate traceable full-cohort figures and participant-level contrasts."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import ttest_1samp


def main() -> None:
    source = Path("results/full-cohort")
    figures = source / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    features = pd.read_parquet(source / "features.parquet")
    feature_column = "base_feature_name" if "base_feature_name" in features.columns else "feature_name"
    entropy = features[features[feature_column].eq("permutation_entropy")]
    participant_means = entropy.groupby(["subject_code", "workload_level"], as_index=False).feature_value.mean()
    contrasts = participant_means.pivot(index="subject_code", columns="workload_level", values="feature_value")
    contrasts["four_minus_one"] = contrasts[4] - contrasts[1]
    statistic = ttest_1samp(contrasts["four_minus_one"].dropna(), 0.0)
    contrasts.to_csv(source / "participant_entropy_contrasts.csv")
    pd.DataFrame([{"feature": "permutation_entropy", "contrast": "4-back minus 1-back", "mean_difference": contrasts.four_minus_one.mean(), "t_statistic": statistic.statistic, "p_value_uncorrected": statistic.pvalue, "n_subjects": len(contrasts)}]).to_csv(source / "statistics.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for subject, group in participant_means.groupby("subject_code"):
        ax.plot(group.workload_level, group.feature_value, marker="o", alpha=0.8, label=subject)
    ax.set(xlabel="N-back workload level", ylabel="Mean per-channel permutation entropy", title="Full released cohort: entropy by workload")
    ax.set_xticks([1, 2, 3, 4]); ax.grid(alpha=0.25); ax.legend(ncol=2, frameon=False)
    fig.tight_layout(); fig.savefig(figures / "entropy_by_workload.png", dpi=180); fig.savefig(figures / "entropy_by_workload.svg"); plt.close(fig)

    models = pd.read_csv(source / "model_evaluations.csv")
    means = models.groupby(["feature_group", "model_name"], as_index=False).balanced_accuracy.mean()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    means.pivot(index="feature_group", columns="model_name", values="balanced_accuracy").plot.bar(ax=ax, rot=0)
    ax.set(ylabel="Mean grouped balanced accuracy", title="Exploratory grouped model comparison"); ax.set_ylim(0, 1); ax.grid(axis="y", alpha=0.25)
    fig.tight_layout(); fig.savefig(figures / "model_comparison.png", dpi=180); fig.savefig(figures / "model_comparison.svg"); plt.close(fig)
    print(f"FIGURES_OK subjects={len(contrasts)} output={figures}")


if __name__ == "__main__": main()
