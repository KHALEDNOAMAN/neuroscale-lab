"""Integrate one verified participant's BIDS metadata and Parquet features into SQLite."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from neuroscale.database.core import connect, initialize


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/sub-001/eeg"))
    parser.add_argument("--features", type=Path, default=Path("results/real-sub001/features.parquet"))
    parser.add_argument("--participants", type=Path, default=Path("research/participants.tsv"))
    parser.add_argument("--output", type=Path, default=Path("results/real-sub001/neuroscale.sqlite"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        args.output.unlink()
    initialize(args.output)
    con = connect(args.output)
    participants = pd.read_csv(args.participants, sep="\t")
    subject = "sub-001"
    participant = participants.loc[participants.participant_id.eq(subject)].iloc[0]
    dataset_id = con.execute(
        "INSERT INTO dataset(name,version,doi,license) VALUES (?,?,?,?)",
        ("Multimodal Cognitive Workload n-back Task, 4 Difficulties", "v1.0.0", "10.82901/nemar.on007169", "CC0"),
    ).lastrowid
    pid = con.execute(
        "INSERT INTO participant(dataset_id,subject_code,age,sex,analysis_included) VALUES (?,?,?,?,?)",
        (dataset_id, subject, float(participant.age), str(participant.sex), int(bool(participant.analysis_included))),
    ).lastrowid
    sid = con.execute("INSERT INTO session(participant_id,session_label) VALUES (?,?)", (pid, "ses-01")).lastrowid
    eeg_json = json.loads((args.input / "sub-001_task-nback_eeg.json").read_text())
    reference = eeg_json.get("EEGReference", "linked ears (Ag/AgCl)")
    eeg_file = args.input / "sub-001_task-nback_eeg.eeg"
    rid = con.execute(
        "INSERT INTO recording(session_id,modality,sampling_frequency,channel_count,reference,source_uri,sha256) VALUES (?,?,?,?,?,?,?)",
        (sid, "EEG", float(eeg_json.get("SamplingFrequency", 250.0)), int(eeg_json.get("EEGChannelCount", 19)), reference, str(eeg_file), sha256(eeg_file)),
    ).lastrowid
    events = pd.read_csv(args.input / "sub-001_task-nback_events.tsv", sep="\t")
    run_id = con.execute(
        "INSERT INTO processing_run(config_json,software_version,seed) VALUES (?,?,?)",
        (json.dumps({"mode": "real-subset", "window_seconds": 1.0, "tutorial_excluded": True, "dropout_policy": "exclude_events_with_dropped_samples"}), "0.2.0", 20261014),
    ).lastrowid
    for _, event in events.iterrows():
        nback = None if pd.isna(event.get("nback_level")) else int(event.nback_level)
        dropped = 0 if pd.isna(event.get("dropped_samples")) else int(event.dropped_samples)
        tutorial = str(event.get("istutorial", "False")).lower() == "true"
        accuracy = None if pd.isna(event.get("response_accuracy")) else int(event.response_accuracy)
        event_id = con.execute(
            "INSERT INTO event(recording_id,onset_seconds,duration_seconds,trial_type,nback_level,is_tutorial,dropped_samples,response_accuracy) VALUES (?,?,?,?,?,?,?,?)",
            (rid, float(event.onset), float(event.duration), str(event.trial_type), nback, int(tutorial), dropped, accuracy),
        ).lastrowid
        included = nback in {1, 2, 3, 4} and not tutorial and dropped == 0 and str(event.trial_type) == f"{nback}-back"
        con.execute(
            "INSERT INTO qc_decision(recording_id,event_id,decision,reason,metric_json) VALUES (?,?,?,?,?)",
            (rid, event_id, "include" if included else "exclude", "eligible_task_event" if included else "tutorial_or_dropout_or_nontrial", json.dumps({"dropped_samples": dropped})),
        )
    features = pd.read_parquet(args.features)
    con.executemany(
        "INSERT INTO feature_record(recording_id,run_id,epoch_index,workload_level,feature_name,feature_value) VALUES (?,?,?,?,?,?)",
        [(rid, run_id, int(row.epoch_index), int(row.workload_level), str(row.feature_name), float(row.feature_value)) for row in features.itertuples()],
    )
    for path in sorted(args.input.iterdir()):
        con.execute("INSERT INTO artifact(run_id,path,bytes,sha256,role) VALUES (?,?,?,?,?)", (run_id, str(path), path.stat().st_size, sha256(path), "source"))
    con.execute("INSERT INTO artifact(run_id,path,bytes,sha256,role) VALUES (?,?,?,?,?)", (run_id, str(args.features), args.features.stat().st_size, sha256(args.features), "derived-features"))
    con.commit()
    included = con.execute("SELECT COUNT(*) FROM qc_decision WHERE decision='include'").fetchone()[0]
    excluded = con.execute("SELECT COUNT(*) FROM qc_decision WHERE decision='exclude'").fetchone()[0]
    feature_count = con.execute("SELECT COUNT(*) FROM feature_record").fetchone()[0]
    print(f"DB_INTEGRATED subject={subject} included_events={included} excluded_events={excluded} features={feature_count} path={args.output}")
    con.close()


if __name__ == "__main__":
    main()
