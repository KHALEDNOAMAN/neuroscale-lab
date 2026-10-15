# Phase 2 audit

## Reproduced baseline

The existing `make verify` target ran successfully before modification: five tests passed, Ruff passed, and the deterministic demo created 936 feature records. The previous real-data artifact contained 5,200 rows for `sub-001` and was not integrated into SQLite.

## Verified defects

1. `permutation_entropy` accepted NaN and infinite values.
2. The spectral implementation used one FFT periodogram despite its Welch-oriented description.
3. Default extraction included `mpe_scale_1`, duplicating permutation entropy.
4. The schema lacked session, artifact, QC, and model-evaluation entities.
5. No grouped ML evaluator or substantive SQL benchmark existed.
6. The previous real-data script was hard-coded to one participant and used an arbitrary 1-second smoke-test window.
7. Dependency versions were specified only as lower bounds.

## Methodological risks

A 1-second epoch has 1 Hz nominal Welch resolution at 250 samples, making delta estimates coarse. The dataset contains many dropout annotations, so retaining all task events would contaminate the analysis. Four participants are sufficient to test grouped software behavior but not to support stable population inference. Mean-across-channel reduction is a provisional spatial summary and can obscure channel-specific effects.

## Repairs completed

The estimator now rejects non-finite input and returns NaN when the number of ordinal vectors is below `m!` by default. Welch PSD uses Hann windows, constant detrending, 50% overlap, density scaling, and explicit `nperseg`. Scale one is excluded from the multiscale feature group. SQLite now records sessions, artifacts, QC decisions, model evaluations, and provenance. A four-participant cohort processor, grouped evaluator, SQL query suite, benchmark, and real-data figures were added.

## Remaining gap

The full 18-participant cohort was not downloaded in this increment. Results are explicitly labeled as a verified four-participant subset. Full-cohort inference remains required before making a generalization claim.
