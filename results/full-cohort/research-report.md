# NeuroScale Lab Phase 3 full-cohort report

## Scope and integrity

The complete released cohort of 18 participants from NEMAR `on007169` v1.0.0 was acquired with resumable downloads and SHA-256 manifests. The final processing protocol preserved 19 EEG channel identities, applied one shared event-level QC classifier, used one-second windows with two 0.5-second Welch segments and 50% overlap, corrected band-boundary integration by interpolation, and exported channelized features to Parquet.

## QC

Across the release, 8665 labeled task events were inspected. 4442 were retained, 1458 tutorials were excluded, 2764 windows overlapped dropout markers, and 1 failed boundary checks. The feature table contains 1,012,776 channel-feature rows.

## Statistical result

The participant-level 4-back minus 1-back permutation-entropy contrast had mean difference 0.003932, standard deviation 0.019073, t statistic 0.875, and uncorrected p-value 0.3940 across 18 participants. This is an exploratory repeated-measures summary; no causal or clinical inference is made.

## Grouped predictive result

| Feature group | Model | Mean balanced accuracy | SD |
|---|---|---:|---:|
| combined | hist_gradient_boosting | 0.2509 | 0.0512 |
| combined | logistic_regression | 0.2616 | 0.0259 |
| combined | majority_baseline | 0.2500 | 0.0000 |
| entropy | hist_gradient_boosting | 0.2492 | 0.0518 |
| entropy | logistic_regression | 0.2533 | 0.0263 |
| entropy | majority_baseline | 0.2500 | 0.0000 |
| spectral | hist_gradient_boosting | 0.2565 | 0.0229 |
| spectral | logistic_regression | 0.2655 | 0.0326 |
| spectral | majority_baseline | 0.2500 | 0.0000 |

Evaluation used five participant-grouped folds. Imputation and scaling were fitted inside training folds. The majority baseline achieved 0.2500 balanced accuracy, the expected chance level for four balanced workload classes. The combined group did not exceed the spectral logistic baseline in this protocol.

## Limitations

The one-second event window is constrained by the 1.0-second stimulus and 0.7-second blank timing. The two-segment Welch configuration improves averaging but gives approximately 2 Hz frequency resolution. Dropout annotations are acquisition-quality markers, not a complete physiological artifact model. Channelized features preserve spatial identity but do not establish a validated regional parcellation. Model selection is fixed and not nested. Findings are observational and exploratory.
