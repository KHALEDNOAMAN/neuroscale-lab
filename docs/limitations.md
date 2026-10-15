# Limitations

This document describes the full-cohort Phase 3 results and the October 15, 2026 QC boundary hotfix. Phase 2 notes elsewhere in the repository are historical records.

- **Cohort size and external validity:** All 18 released participants were processed, but this is still one experiment with a modest number of independent participants. External-dataset replication has not been performed.
- **EEG window and spectral resolution:** Each stimulus-aligned epoch is one second. The Phase 3 Welch configuration uses `nperseg=125` at 250 Hz (approximately 2 Hz frequency resolution), with a Hann window and 50% overlap. Low-frequency bandpower, especially delta power, is poorly resolved.
- **Quality control and potential selection bias:** Of 8,665 labeled task events, 4,442 were retained. Tutorial, annotated-dropout-overlapping, and one boundary-invalid epoch were excluded. Dropout annotations are not comprehensive detection of blink, muscle, or motion artifacts. The possibility of workload-dependent exclusion and selection bias requires further investigation.
- **Spatial interpretation:** Channel identity is preserved for 19 EEG channels per participant. No validated neurophysiological regional parcellation or spatial complexity result is claimed.
- **Machine learning:** Five-fold grouped evaluation prevents participant overlap, but fixed model settings were used rather than nested hyperparameter tuning. Mean balanced accuracy was near the four-class baseline. No incremental predictive improvement from entropy features was demonstrated under this protocol; this is not evidence of universal ineffectiveness.
- **Statistical inference:** Exploratory contrasts are not causal or clinical findings. The released cohort is too small for strong generalization or high-resolution subgroup inference. Broader sensitivity analyses and independent replication remain necessary.
- **Operational verification:** The original full-cohort analysis was performed on Linux. On macOS Python 3.13, the QC-hotfixed source passed 18 automated tests and Ruff checks. Docker execution was not verified.
- **Post-release database correction:** The v0.1.0 SQLite Release artifact has the boundary-invalid `sub-011` event `11986` recorded as `exclude / boundary_invalid`. The repair was checked using SQLite integrity and foreign-key tests. This metadata repair does not recalculate extracted features or machine-learning results.

See `docs/statistical-analysis-plan.md`, `docs/verification-matrix.md`, and `results/full-cohort/research-report.md` for methods and evidence.
