# Phase 3 verification matrix

Environment: Ubuntu 24.04 sandbox, Python 3.12, NumPy 2.5.3, SciPy 1.18.1, scikit-learn 1.9.1, MNE 1.13.2, pytest 9.1.1, Ruff 0.17.0. Exact package pins are in `requirements.lock`.

| Area | Status | Exact command / artifact | Observed result and limitation |
|---|---|---|---|
| Phase 2 baseline reproduction | PASS | `make verify` before Phase 3 changes | 12 prior tests and demo reproduced |
| Finite entropy validation | PASS | `pytest -q` | NaN/Inf rejected; multidimensional arrays rejected |
| Entropy normalization and degeneracy | PASS | `tests/test_entropy.py`, `tests/test_scientific_features.py` | Bounds and constant/monotone behavior verified |
| Welch PSD known-signal tests | PASS | `tests/test_scientific_features.py` | 10 Hz peak and alpha concentration verified |
| Band-boundary integration | PASS | `src/neuroscale/features/spectral.py` | Interpolated boundaries included in trapezoidal integration |
| Fold-local imputation and scaling | PASS | `src/neuroscale/models/evaluate.py`, adversarial test | Training pipelines own imputation/scaling; held-out data is not fit-visible |
| Group disjointness | PASS | `tests/test_models.py`, runtime assertions | Every train/test subject set is disjoint |
| Shared event QC | PASS | `src/neuroscale/ingestion/qc.py`, `tests/test_qc.py` | NaN labels, tutorial, dropout, and clean events covered |
| Full cohort acquisition | PASS | `scripts/acquire_dataset.py` | 18 released participants acquired with SHA-256 manifests; raw data excluded from archive |
| Full cohort processing | PASS | `scripts/run_cohort_subset.py` | 18 participants; 8,665 task events; 4,442 retained; 1,012,776 channel-feature rows |
| Channel provenance | PASS | `results/full-cohort/features.parquet` and SQLite `channel` | 19 EEG channels per participant retained; no unconditional channel averaging |
| SQLite referential integrity | PASS | `PRAGMA foreign_key_check` through `database.core.connect` | 18 participants; 342 channels; 19,095 events; 1,012,776 features; 45 evaluations; zero violations |
| Idempotent integration | PASS | rerun `scripts/integrate_cohort.py` on existing output | Existing populated DB is preserved and reported as already integrated |
| Grouped model evaluation | PASS | `evaluate_grouped(features,n_splits=5)` | 45 results: three feature groups × three models × five folds |
| Statistical contrast | PASS | `results/full-cohort/statistics.csv` | 18-participant exploratory 4-back minus 1-back contrast |
| Scientific figures | PASS | `results/full-cohort/figures/*.svg` | Full-cohort SVG figures generated from recorded outputs |
| SQL benchmark | PASS | `scripts/benchmark_sql.py results/full-cohort/neuroscale.sqlite` | 160 timings per condition and plan difference recorded; indexed aggregate was slower here, so no speedup is claimed |
| Automated tests | PASS | `pytest -q` | 16 passed during original Phase 3 verification; 18 passed after the QC hotfix on macOS Python 3.13 |
| Lint | PASS | `ruff check --no-cache src tests scripts` | All checks passed |
| Docker build | NOT RUN | `docker build` | Docker unavailable in current sandbox |
| Nested hyperparameter tuning | NOT RUN | Not implemented | Fixed transparent models used |
| Causal or clinical inference | NOT RUN | Outside scope | Results are observational and exploratory |

## Post-hotfix verification (2026-10-15)

These checks supplement, rather than retroactively replace, the Linux Phase 3 evidence above.

| Area | Status | Evidence | Observation |
|---|---|---|---|
| Hotfixed tests on macOS | PASS | `python -m pytest -q` | 18 passed using Python 3.13 |
| Hotfixed lint on macOS | PASS | `python -m ruff check src tests scripts` | All checks passed |
| Boundary QC correction | PASS | `scripts/repair_qc_boundary.py` on the full-cohort SQLite database | `sub-011`, event `11986`, epoch `1648`: `exclude / boundary_invalid`; database backup created |
| Database integrity after correction | PASS | `PRAGMA integrity_check`; `PRAGMA foreign_key_check` | `ok`; zero violations |
| Hotfix GitHub CI | PASS | [CI run 38729980236](https://github.com/SoheilGtex/neuroscale-lab/actions/runs/38729980236) | `ce85f77` successfully verified |
| README GitHub CI | PASS | [CI run 38732006785](https://github.com/SoheilGtex/neuroscale-lab/actions/runs/38732006785) | `f9c5d45` successfully verified |
| Docker execution | NOT RUN | No executed Docker build provided | Do not treat a Dockerfile as a verified build |

The corrected v0.1.0 release database is distributed separately as `neuroscale-full-cohort-v0.1.0.zip` with SHA-256 `b8cf06511733404dc44696794578307c2f335208e3ddde9ac5379b832f841efd`. No raw EEG processing was independently rerun on macOS during the hotfix verification.
