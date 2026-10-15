"""Extract a bounded participant-level feature table from verified BrainVision files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mne
import pandas as pd

from neuroscale.features.extract import extract_features


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("data/raw/sub-001/eeg"))
    ap.add_argument("--output", type=Path, default=Path("results/real-sub001"))
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    vhdr = args.input / "sub-001_task-nback_eeg.vhdr"
    events_path = args.input / "sub-001_task-nback_events.tsv"
    raw = mne.io.read_raw_brainvision(vhdr, preload=True, verbose="ERROR")
    eeg = mne.pick_types(raw.info, eeg=True, exclude="bads")
    events = pd.read_csv(events_path, sep="\t")
    selected = events[
        events["nback_level"].notna()
        & events["istutorial"].astype(str).str.lower().eq("false")
        & events["trial_type"].isin(["1-back", "2-back", "3-back", "4-back"])
    ].copy()

    rows = []
    sfreq = float(raw.info["sfreq"])
    for epoch_index, event in selected.reset_index(drop=True).iterrows():
        start = max(0, round(float(event.onset) * sfreq))
        stop = min(raw.n_times, start + round(1.0 * sfreq))
        if stop - start < int(sfreq):
            continue
        # Channel averaging is a deliberately simple smoke-test reduction, not a final spatial model.
        signal = raw.get_data(picks=eeg, start=start, stop=stop).mean(axis=0)
        features = extract_features(signal, sfreq)
        for name, value in features.items():
            rows.append({
                "subject_code": "sub-001",
                "epoch_index": int(epoch_index),
                "onset_seconds": float(event.onset),
                "workload_level": int(event.nback_level),
                "feature_name": name,
                "feature_value": float(value),
            })
    table = pd.DataFrame(rows)
    table.to_parquet(args.output / "features.parquet", index=False)
    summary = table.groupby(["workload_level", "feature_name"], as_index=False)["feature_value"].agg(["mean", "std", "count"]).reset_index()
    summary.to_csv(args.output / "summary.csv", index=False)
    manifest = {"source_files": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(args.input.iterdir())}, "sfreq": sfreq, "eeg_channels": len(eeg), "selected_events": len(selected), "feature_rows": len(table), "tutorial_events_excluded": True, "channel_reduction": "mean across EEG channels", "window_seconds": 1.0}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
