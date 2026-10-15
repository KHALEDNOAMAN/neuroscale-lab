# Future research

1. Implement a BIDS subset ingestor that validates `*_events.tsv` against `task-nback_events.json`, rejects dropout-contaminated epochs, and records hashes.
2. Compare permutation entropy against spectral entropy and multiscale variants under an explicitly preregistered parameter grid, with participant-level bootstrap intervals.
3. Evaluate spectral-only, entropy-only, and combined models using nested grouped cross-validation and a held-out participant set where sample size permits.
4. Quantify incremental value with out-of-sample likelihood or balanced-accuracy differences, not only p-values.
5. Study robustness to reference choice, epoch duration, sampling rate, and missing channels.
6. Extend the relational experiment registry so each result can be traced to exact source files, preprocessing parameters, software versions, and random seeds.
