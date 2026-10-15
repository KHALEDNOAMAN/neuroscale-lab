# Real-data subset report

## Scope

This report describes a bounded smoke test on participant `sub-001` from NEMAR `on007169` v1.0.0. It is an execution check for the ingestion boundary and feature code, not a confirmatory scientific analysis.

The BrainVision recording was parsed at 250 Hz with 19 EEG channels. The BIDS events contained 121, 120, 120, and 120 task events for levels 1–4, plus tutorial and dropout markers. The extraction selected exactly 400 non-tutorial events, 100 per workload level, and used a 1.0-second window from event onset. The signal was reduced by averaging the 19 EEG channels. This spatial reduction is explicitly provisional.

## Descriptive values

| Feature | 1-back | 2-back | 3-back | 4-back |
|---|---:|---:|---:|---:|
| Permutation entropy mean | 0.8369 | 0.8132 | 0.8374 | 0.8868 |
| Relative theta mean | 0.1618 | 0.1657 | 0.1619 | 0.1604 |
| Relative alpha mean | 0.1393 | 0.1112 | 0.1075 | 0.1068 |
| Relative beta mean | 0.1601 | 0.1702 | 0.1397 | 0.1442 |

Each cell is the mean of 100 epoch-level values from one participant. The standard deviations and full feature table are in `results/real-sub001/summary.csv` and `results/real-sub001/features.parquet`.

## Interpretation boundary

These values do not establish a monotonic workload relationship, statistical significance, predictive utility, or participant-level generalization. The apparent non-monotonic entropy pattern is compatible with subject-specific variation, task timing, artifact, reference effects, and the provisional channel-averaging reduction. A valid research analysis must repeat the pipeline across released participants, define artifact/dropout handling in advance, and use participant-grouped inference and evaluation.
