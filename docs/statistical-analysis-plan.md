# Statistical analysis plan v0.3.0

## Primary question

Do entropy features improve prediction of cognitive workload beyond conventional spectral EEG features for previously unseen participants?

## Analysis unit

The participant is the independent generalization unit. Epochs are repeated observations nested within participant. Channel-level values are features within an epoch, not independent subjects.

## Primary evaluation

The primary predictive comparison is participant-grouped cross-validation using three prespecified feature groups: spectral-only, entropy-only, and combined. Fixed regularized multinomial logistic regression is the primary model. A majority-class baseline is mandatory. Histogram gradient boosting is secondary and exploratory. Imputation and scaling are fit inside the training fold. Test participants never occur in training folds.

## Descriptive inference

For each participant, workload-level feature means are computed after QC. The primary descriptive contrast is 4-back minus 1-back permutation entropy. Report the participant-level mean difference, standard deviation, confidence interval, and individual contrasts. With 18 participants this remains an observational repeated-measures analysis; no causal claim is made.

## Multiplicity and exploratory status

The primary contrast is prespecified. Additional channels, bands, scales, and preprocessing variants are exploratory and require multiplicity control or explicit family-wise reporting. The four-participant Phase 2 result is superseded by the Phase 3 full-cohort result only after its execution and verification.

## Robustness

Sensitivity dimensions include channel-preserving versus regional aggregation, dropout-window policy, epoch length constrained by the 1.0-second stimulus and 0.7-second blank timing, entropy order and delay, and Welch segment length. No configuration may be selected because it produces the most favorable held-out result.

## Limitations

The dataset is a single experiment with a modest participant count. Dropout markers are acquisition-quality annotations rather than a complete physiological artifact model. The protocol does not support diagnostic or clinical claims.
