# NeuroScale Lab - Experiment Guide

## Overview
Reproducible EEG complexity analysis and cross-subject workload modeling.

## Pipeline
```
Raw EEG --> Preprocessing --> Feature Extraction --> Complexity Metrics --> Classification
              |                    |                       |
          Filtering           Band Power            Entropy Measures
          Artifact Removal    Connectivity           Fractal Dimension
```

## Complexity Metrics
| Metric | Description |
|--------|-------------|
| Sample Entropy | Signal regularity |
| Permutation Entropy | Ordinal pattern complexity |
| Fractal Dimension | Signal self-similarity |
| Lempel-Ziv | Algorithmic complexity |

## Setup
```bash
git clone https://github.com/SoheilGtex/neuroscale-lab.git
cd neuroscale-lab
pip install -r requirements.txt
```

## Reproducibility
- All random seeds fixed
- Data versioning with DVC
- Environment: requirements.txt + Docker