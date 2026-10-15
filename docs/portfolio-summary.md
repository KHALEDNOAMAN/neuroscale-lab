# Portfolio summary

NeuroScale Lab is a reproducible scientific-computing repository for testing whether temporal EEG complexity measures add predictive information beyond spectral features in an n-back workload task. The implemented release includes a finite-input permutation-entropy estimator, multiscale coarse-graining, Welch spectral estimation, per-channel feature extraction, explicit event-level QC, normalized SQLite provenance, Parquet analytical storage, grouped cross-participant evaluation, SQL benchmarks, and reproducible figures.

The Phase 3 release processes all 18 released participants from the pinned NEMAR dataset. Results remain observational and non-clinical. The repository does not claim peer review, state-of-the-art performance, or causal interpretation. The exact cohort, QC, model, and statistical evidence are in the generated reports and verification manifest.

Suggested CV bullets:

- Implemented and numerically tested finite-input permutation entropy, multiscale coarse-graining, and Welch PSD features with explicit tie, normalization, boundary, and effective-window policies.
- Built a reproducible EEG data platform that preserves channel identity, applies shared event-level dropout QC, records source hashes, and integrates Parquet features with normalized SQLite provenance and SQL analysis.
- Evaluated spectral-only, entropy-only, combined, and majority-baseline models using participant-grouped cross-validation with fold-local imputation and scaling, reporting uncertainty and limitations rather than optimized headline scores.

Example statement-of-purpose paragraph: “I developed NeuroScale Lab to connect numerical methods, data engineering, and computational neuroscience. The project required me to distinguish computational validity from estimator reliability, preserve participant-level independence, and make the evidence chain from BIDS files to model evaluation inspectable. The resulting work strengthened my interest in statistical learning for scientific signals, especially where methodological choices can dominate apparent findings.”

Representation boundary: describe the project as AI-assisted scientific software developed and audited by the owner; do not represent generated code as exclusively human-authored or claim publications, appointments, or independent scientific novelty without external evidence.
