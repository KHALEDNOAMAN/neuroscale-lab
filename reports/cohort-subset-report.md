# NeuroScale Lab Phase 2 cohort-subset report

## Abstract

A bounded four-participant subset of the verified CC0 NEMAR n-back EEG dataset was processed with explicit event and dropout quality control. The pipeline retained 1,031 of 1,924 task events and produced 12,372 feature records. Welch spectral features and permutation-entropy features were evaluated with participant-grouped four-fold cross-validation. This report is an engineering and exploratory analysis result, not a full-cohort claim.

## Data and QC

The processed participants were `sub-001` through `sub-004`, each with 19 EEG channels sampled at 250 Hz. The processor excluded tutorial events and 1-second windows intersecting dropout markers. Retained event counts were 263, 308, 222, and 238 respectively. No epoch was excluded for boundary failure. The complete per-participant QC table is `results/cohort-subset/qc_report.csv`; source hashes are in `results/cohort-subset/manifest.json`.

## Methods

Each retained event used a 1-second onset window and mean reduction across EEG channels. Welch PSD used a Hann window, constant detrending, 50% overlap, density scaling, and an explicit 2-second requested segment clipped to the 1-second epoch. Therefore the effective segment is 250 samples with approximately 1 Hz resolution. Delta power is consequently coarse and should not be overinterpreted.

Permutation entropy used order three, delay one, stable tie-breaking, finite-input validation, normalization by `log(3!)`, and the default minimum of six ordinal vectors. Multiscale features used scales 2, 4, and 8; scale 1 was intentionally omitted because it duplicates ordinary permutation entropy.

Models were regularized logistic regression and histogram gradient boosting. Feature groups were spectral-only, entropy-only, and combined. Scaling was inside the logistic pipeline. Four-fold `GroupKFold` held out participants rather than epochs. This is grouped evaluation, not nested hyperparameter optimization.

## Executed results

The participant-level 4-back minus 1-back entropy contrast had mean `0.0245`, t statistic `2.435`, and uncorrected p-value `0.0930` across four participants. This is exploratory, low-powered, and does not establish a workload effect.

Mean grouped balanced accuracy was:

| Feature group | Logistic regression | Histogram gradient boosting |
|---|---:|---:|
| Spectral | 0.3127 | 0.2625 |
| Entropy | 0.2899 | 0.2159 |
| Combined | 0.2976 | 0.2597 |

On this subset and protocol, the combined group did not exceed the spectral logistic baseline. This is not evidence that entropy is useless; it is a bounded result under one preprocessing configuration and four participants.

Figures are in `results/cohort-subset/figures/`. The feature table, model fold results, statistics, QC report, SQLite database, and source manifest form the traceability chain.

## Limitations

The subset is not the full 18-participant release. The short epoch limits low-frequency spectral resolution. The channel-mean reduction is not a validated spatial model. Dropout overlap was handled by excluding windows, but artifact rejection beyond explicit dropout annotations is not yet implemented. Grouped evaluation did not tune hyperparameters in nested inner folds. No multiplicity correction was applied because the displayed contrast is a single exploratory summary.
