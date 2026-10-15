# Dataset audit

## Decision

**[Definitive] Feasible for the stated research questions, with caveats.** The NEMAR record for `on007169` exposes a BIDS-converted EEG dataset with four n-back levels and 18 released participants. The OpenNeuro metadata page identifies the upstream dataset as `ds007169`, CC0, with 18 participants and one session. The GitHub mirror documents 20 recorded participants, with `sub-013` and `sub-017` excluded for data-quality failures.

## Verified facts

- NEMAR copy: `v1.0.0`, DOI `10.82901/nemar.on007169`.
- Upstream OpenNeuro snapshot: DOI `10.18112/openneuro.ds007169.v1.0.5`.
- License: CC0.
- EEG: 19-channel 10–20 montage, 250 Hz, continuous BrainVision files.
- Conditions: `1-back`, `2-back`, `3-back`, `4-back`; tutorial markers are separately represented.
- Event semantics: the BIDS event dictionary defines `trial_type`, `nback_level`, `marker_stream`, response accuracy, tutorial flags, and dropped-sample annotations.
- Dataset-level metadata downloaded into `research/`: `participants.tsv`, `dataset_description.json`, directory index, participant-001 directory listing, and event/channel JSON files.

## Risks

The OpenNeuro page showed 54 BIDS warnings for the inspected version. The raw dataset includes acquisition dropout annotations and no epoch rejection. The four levels are repeated within participant, so epochs cannot be treated as independent participants. Any analysis must use participant-grouped validation and participant-level uncertainty summaries.

## Sources

1. https://nemar.org/dataset/on007169
2. https://openneuro.org/datasets/ds007169/versions/1.0.3/metadata
3. https://github.com/OpenNeuroDatasets/ds007169
4. https://data.nemar.org/on007169/v1.0.0/participants.tsv
5. https://data.nemar.org/on007169/v1.0.0/task-nback_events.json
