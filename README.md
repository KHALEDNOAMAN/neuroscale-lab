# NeuroScale Lab

*A reproducible scientific data platform for multiscale neural complexity and cognitive workload modeling.*

## Research questions

1. Do permutation entropy and multiscale permutation entropy add information beyond conventional EEG spectral features when workload is varied by a 1–4-back task?
2. Do any associations or predictive gains generalize to participants not seen during training?

The project is designed to support negative and inconclusive findings. The synthetic demo verifies software plumbing only; it is not evidence about EEG or workload.

## Verified primary dataset

The starting dataset is **Multimodal Cognitive Workload n-back Task, 4 Difficulties**, NEMAR `on007169`, version `v1.0.0`, derived from OpenNeuro `ds007169` version `1.0.5`. The NEMAR record reports 18 released participants, 19 EEG channels, 250 Hz sampling, four n-back conditions, CC0 licensing, and two exclusions for data-quality failures. The BIDS event dictionary defines `nback_level`, `trial_type`, response fields, tutorial flags, and dropout annotations. See `docs/dataset-audit.md` for the evidence record and citations.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
make test
make lint
make demo
```

The demo creates `results/demo/neuroscale.sqlite` and inserts explicitly labeled synthetic epochs and derived features. It is deterministic under seed `20261014`.

## Full-cohort release

The current verified empirical run covers all 18 released participants. It retained 4,442 of 8,665 labeled task events after excluding tutorials, dropout-overlapping windows, and one boundary-invalid epoch. Per-channel extraction generated 1,012,776 feature rows, integrated them into SQLite, and evaluated spectral-only, entropy-only, combined, and majority-baseline models with participant-grouped five-fold cross-validation. See `results/full-cohort/research-report.md`, `docs/verification-manifest.json`, and `docs/statistical-analysis-plan.md`.

```bash
make test
make lint
make demo
PYTHONPATH=src python3 scripts/run_cohort_subset.py --subjects sub-001 sub-002 sub-003 sub-004
PYTHONPATH=src python3 - <<'PY'
import pandas as pd
from neuroscale.models.evaluate import evaluate_grouped
table = pd.read_parquet('results/full-cohort/features.parquet')
print(evaluate_grouped(table, n_splits=4))
PY
PYTHONPATH=src python3 scripts/integrate_cohort.py --features results/full-cohort/features.parquet --qc results/full-cohort/qc_report.csv --models results/full-cohort/model_evaluations.csv --output results/full-cohort/neuroscale.sqlite
python3 scripts/make_figures.py
```

The public raw files are downloaded separately and excluded from release archives. The full-cohort result is observational and exploratory; it is not a clinical or causal claim.

## Repository map

- `src/neuroscale/features/`: permutation entropy, multiscale coarse-graining, and spectral features.
- `src/neuroscale/database/`: SQLite initialization with foreign keys, checks, indexes, and an analysis view.
- `tests/`: numerical and relational integrity tests.
- `docs/`: dataset audit, scientific methods, architecture, limitations, and reproducibility notes.
- `research/`: downloaded public metadata used to audit the dataset; raw EEG is intentionally not committed.

## Real-data status

The public dataset is accessible and its metadata was downloaded and inspected. Phase 3 processes the complete released cohort with explicit dropout QC, Welch PSD, channel-preserving features, grouped evaluation, SQLite integration, SQL benchmarks, and generated figures. The final report records the exact limitations and exploratory status.

## License and citation

Software is MIT licensed. The dataset is CC0. Cite the dataset separately:

> Barras, M., & Booth, L. (2026). *Multimodal Cognitive Workload n-back Task, 4 Difficulties* (Version v1.0.0) [Data set]. NEMAR. https://doi.org/10.82901/nemar.on007169

## Quality policy

Every validation item is classified as `PASS`, `FAIL`, or `NOT RUN`. No scientific conclusion is reported until it comes from downloaded, verified data and a participant-grouped evaluation.
