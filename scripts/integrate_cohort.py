"""Integrate full-cohort artifacts into the normalized research database."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from neuroscale.database.core import connect, initialize
from neuroscale.ingestion.qc import classify_event


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--features", type=Path, default=Path("results/full-cohort/features.parquet"))
    parser.add_argument("--qc", type=Path, default=Path("results/full-cohort/qc_report.csv"))
    parser.add_argument("--models", type=Path, default=Path("results/full-cohort/model_evaluations.csv"))
    parser.add_argument("--participants", type=Path, default=Path("research/participants.tsv"))
    parser.add_argument("--output", type=Path, default=Path("results/full-cohort/neuroscale.sqlite"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        existing = connect(args.output)
        if existing.execute("SELECT COUNT(*) FROM participant").fetchone()[0] > 0:
            print(f"DB_ALREADY_INTEGRATED path={args.output}")
            existing.close()
            return
        existing.close()
    initialize(args.output)
    con = connect(args.output)
    dataset_id = con.execute("INSERT INTO dataset(name,version,doi,license) VALUES (?,?,?,?)", ("Multimodal Cognitive Workload n-back Task, 4 Difficulties", "v1.0.0", "10.82901/nemar.on007169", "CC0")).lastrowid
    participants = pd.read_csv(args.participants, sep="\t").set_index("participant_id")
    features = pd.read_parquet(args.features)
    run_id = con.execute("INSERT INTO processing_run(config_json,software_version,seed) VALUES (?,?,?)", (json.dumps({"mode":"full-cohort","subjects":sorted(features.subject_code.unique().tolist()),"dropout_policy":"exclude_windows_intersecting_dropout_markers","window_seconds":1.0,"nperseg":125,"channel_policy":"per-channel"}), "0.3.0", 20261015)).lastrowid
    recording_ids = {}
    channel_ids = {}
    for subject in sorted(features.subject_code.unique()):
        row = participants.loc[subject]
        pid = con.execute("INSERT INTO participant(dataset_id,subject_code,age,sex,analysis_included) VALUES (?,?,?,?,?)", (dataset_id, subject, float(row.age), str(row.sex), int(bool(row.analysis_included)))).lastrowid
        sid = con.execute("INSERT INTO session(participant_id,session_label) VALUES (?,?)", (pid, "ses-01")).lastrowid
        eeg_dir = args.raw / subject / "eeg"; prefix = f"{subject}_task-nback"
        eeg_meta = json.loads((eeg_dir / f"{prefix}_eeg.json").read_text())
        eeg_file = eeg_dir / f"{prefix}_eeg.eeg"
        rid = con.execute("INSERT INTO recording(session_id,modality,sampling_frequency,channel_count,reference,source_uri,sha256) VALUES (?,?,?,?,?,?,?)", (sid,"EEG",float(eeg_meta.get("SamplingFrequency",250)),int(eeg_meta.get("EEGChannelCount",19)),"linked ears (Ag/AgCl)",str(eeg_file),sha256(eeg_file))).lastrowid
        recording_ids[subject] = rid
        channel_names = sorted(features.loc[features.subject_code.eq(subject), "channel_name"].unique())
        channel_ids[subject] = {}
        for channel_name in channel_names:
            channel_ids[subject][channel_name] = con.execute("INSERT INTO channel(recording_id,name) VALUES (?,?)", (rid, str(channel_name))).lastrowid
        events = pd.read_csv(eeg_dir / f"{prefix}_events.tsv", sep="\t")
        dropout_onsets = events.loc[events.trial_type.eq("dropped_samples"), "onset"].astype(float).tolist()
        for _, event in events.iterrows():
            dropped = 0 if pd.isna(event.get("dropped_samples")) else int(event.dropped_samples)
            decision = classify_event(event, dropout_onsets, 1.0)
            level = decision.level
            tutorial = decision.tutorial
            accuracy = None if pd.isna(event.get("response_accuracy")) else int(event.response_accuracy)
            eid = con.execute("INSERT INTO event(recording_id,onset_seconds,duration_seconds,trial_type,nback_level,is_tutorial,dropped_samples,response_accuracy) VALUES (?,?,?,?,?,?,?,?)", (rid,float(event.onset),float(event.duration),str(event.trial_type),level,int(tutorial),dropped,accuracy)).lastrowid
            con.execute("INSERT INTO qc_decision(recording_id,event_id,decision,reason,metric_json) VALUES (?,?,?,?,?)", (rid,eid,"include" if decision.include else "exclude",decision.reason,json.dumps({"dropout_overlap":decision.dropout_overlap})))
        for path in sorted(eeg_dir.iterdir()):
            con.execute("INSERT INTO artifact(run_id,path,bytes,sha256,role) VALUES (?,?,?,?,?)", (run_id,str(path),path.stat().st_size,sha256(path),"source"))
    for row in features.itertuples():
        con.execute("INSERT INTO feature_record(recording_id,channel_id,run_id,epoch_index,workload_level,feature_name,feature_value) VALUES (?,?,?,?,?,?,?)", (recording_ids[row.subject_code],channel_ids[row.subject_code][row.channel_name],run_id,int(row.epoch_index),int(row.workload_level),str(row.feature_name),float(row.feature_value)))
    for row in pd.read_csv(args.models).itertuples():
        con.execute("INSERT INTO model_evaluation(run_id,feature_group,model_name,fold_id,test_subjects_json,balanced_accuracy,macro_f1,confusion_matrix_json) VALUES (?,?,?,?,?,?,?,?)", (run_id,row.feature_group,row.model_name,int(row.fold_id),json.dumps(str(row.test_subjects).split(",")),float(row.balanced_accuracy),float(row.macro_f1),str(row.confusion_matrix)))
    for artifact in [args.features,args.qc,args.models]:
        con.execute("INSERT INTO artifact(run_id,path,bytes,sha256,role) VALUES (?,?,?,?,?)", (run_id,str(artifact),artifact.stat().st_size,sha256(artifact),"derived"))
    con.commit()
    print("DB_COHORT_OK", {"subjects":len(recording_ids),"events":con.execute("SELECT COUNT(*) FROM event").fetchone()[0],"features":con.execute("SELECT COUNT(*) FROM feature_record").fetchone()[0],"evaluations":con.execute("SELECT COUNT(*) FROM model_evaluation").fetchone()[0]})
    con.close()


if __name__ == "__main__": main()
