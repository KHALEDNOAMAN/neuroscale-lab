# Full-cohort model reevaluation (2026-10-15)

## Status

**Corrected exploratory model results, not a new validated scientific discovery.**
This package does not overwrite the historical `results/full-cohort/model_evaluations.csv`
or the previously published GitHub releases.

## Method and provenance

- Evaluation code commit: `09faa658305a6c300055d3173fc927cebd7f7a7e`
- Source: 18 participants, 4,442 retained epochs, 1,012,776 channel-feature rows
- Five participant-grouped folds; same held-out participants as historical evaluation
- Feature counts: spectral 152; entropy 76 (including 57 channel-level MPE columns); combined 228
- Entire corrected CSV was byte-identical across two executions in one environment
- Original and corrected source hashes, dependencies and system details are in `provenance.json`

## Fold-mean balanced accuracy

| Feature set | Model | Historical | Corrected | Delta (percentage points) |
|---|---|---:|---:|---:|
| combined | hist_gradient_boosting | 0.25094 | 0.25094 | +0.000 |
| combined | logistic_regression | 0.26161 | 0.26225 | +0.064 |
| combined | majority_baseline | 0.25000 | 0.25000 | +0.000 |
| entropy | hist_gradient_boosting | 0.24922 | 0.23232 | -1.690 |
| entropy | logistic_regression | 0.25329 | 0.24239 | -1.089 |
| entropy | majority_baseline | 0.25000 | 0.25000 | +0.000 |
| spectral | hist_gradient_boosting | 0.25649 | 0.25649 | +0.000 |
| spectral | logistic_regression | 0.26549 | 0.26616 | +0.067 |
| spectral | majority_baseline | 0.25000 | 0.25000 | +0.000 |

## Interpretation and limitations

The corrected entropy-only logistic and gradient-boosting models score below the 0.25
four-class reference level on this run. Adding entropy features to spectral
features did not improve logistic regression mean balanced accuracy in this
participant-grouped evaluation. These observations do not establish that
entropy features lack predictive value in other protocols or datasets.

The spectral logistic model also changed slightly from the historical run
despite unchanged spectral feature selection. This discrepancy is not explained
by fold assignment, which was checked to be identical; an execution-environment
effect is possible but not confirmed. The repeatability demonstration only covers
two runs within the present environment, not cross-platform replication.

There is no evidence here of a statistically significant gain or loss. Fold
measurements are not independent study participants, and this report provides
no confirmatory paired inference or clinically applicable conclusions.

## Files

- `model_evaluations_corrected.csv`: corrected 45 fold/model evaluations
- `fold_comparison.csv`: paired fold-level historical-versus-corrected differences
- `summary_comparison.csv`: independently calculated group mean differences
- `provenance.json`: source checksums, exact code commit, and execution environment
- `model_accuracy_comparison.png`: visualization of historical and corrected means
