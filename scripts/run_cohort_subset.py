"""Process a BIDS/BrainVision cohort with explicit, shared event QC."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mne
import pandas as pd

from neuroscale.features.extract import extract_features
from neuroscale.ingestion.qc import classify_event


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def process_subject(subject: str, root: Path, window_seconds: float) -> tuple[pd.DataFrame, dict]:
    eeg_dir = root / subject / "eeg"
    prefix = f"{subject}_task-nback"
    raw = mne.io.read_raw_brainvision(eeg_dir / f"{prefix}_eeg.vhdr", preload=True, verbose="ERROR")
    eeg_picks = mne.pick_types(raw.info, eeg=True, exclude="bads")
    eeg_names = [raw.ch_names[index] for index in eeg_picks]
    events = pd.read_csv(eeg_dir / f"{prefix}_events.tsv", sep="\t")
    dropout_onsets = events.loc[events.trial_type.eq("dropped_samples"), "onset"].astype(float).tolist()
    rows = []
    counts = {"task_events": 0, "included": 0, "tutorial_excluded": 0, "dropout_excluded": 0, "boundary_excluded": 0}
    sfreq = float(raw.info["sfreq"])
    window_samples = round(window_seconds * sfreq)
    nperseg = max(4, window_samples // 2)
    for epoch_index, event in events.reset_index(drop=True).iterrows():
        decision = classify_event(event, dropout_onsets, window_seconds)
        if decision.level is None:
            continue
        counts["task_events"] += 1
        if not decision.include:
            counts["tutorial_excluded" if decision.reason == "tutorial_event" else "dropout_excluded"] += 1
            continue
        onset = float(event.onset)
        start = round(onset * sfreq)
        stop = start + window_samples
        if start < 0 or stop > raw.n_times:
            counts["boundary_excluded"] += 1
            continue
        counts["included"] += 1
        signal = raw.get_data(picks=eeg_picks, start=start, stop=stop)
        for channel_name, channel_signal in zip(eeg_names, signal, strict=True):
            channel_features = extract_features(channel_signal, sfreq, nperseg=nperseg)
            for name, value in channel_features.items():
                if pd.notna(value):
                    rows.append({"subject_code": subject, "epoch_index": int(epoch_index), "onset_seconds": onset, "workload_level": decision.level, "channel_name": channel_name, "feature_name": f"{channel_name}__{name}", "base_feature_name": name, "feature_value": float(value)})
    manifest = {"subject_code": subject, "sampling_frequency": sfreq, "eeg_channels": len(eeg_picks), "window_seconds": window_seconds, "nperseg": nperseg, "effective_welch_segments": 2, "qc": counts, "channel_policy": "preserve each EEG channel; no unconditional channel averaging", "source_files": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(eeg_dir.iterdir())}}
    return pd.DataFrame(rows), manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="+", default=["sub-001", "sub-002", "sub-003", "sub-004"])
    parser.add_argument("--input", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("results/cohort-subset"))
    parser.add_argument("--window-seconds", type=float, default=1.0)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    tables, manifests = [], []
    for subject in args.subjects:
        table, manifest = process_subject(subject, args.input, args.window_seconds)
        tables.append(table)
        manifests.append(manifest)
        print(json.dumps(manifest["qc"], sort_keys=True), flush=True)
    features = pd.concat(tables, ignore_index=True)
    features.to_parquet(args.output / "features.parquet", index=False)
    qc = pd.DataFrame([{**m["qc"], "subject_code": m["subject_code"]} for m in manifests])
    qc.to_csv(args.output / "qc_report.csv", index=False)
    (args.output / "manifest.json").write_text(json.dumps({"subjects": manifests, "feature_rows": len(features), "policy": "shared QC; tutorials and windows intersecting dropout markers excluded; 1-second windows; two 0.5-second Welch segments with 50% overlap; per-channel features"}, indent=2) + "\n")
    print(f"COHORT_OK subjects={len(manifests)} feature_rows={len(features)} output={args.output}")


if __name__ == "__main__":
    main()
