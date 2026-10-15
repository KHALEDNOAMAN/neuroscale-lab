from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from neuroscale.database.core import connect, initialize, register_demo
from neuroscale.features.extract import extract_features


def run_demo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    db_path = root / "neuroscale.sqlite"
    if db_path.exists():
        db_path.unlink()
    initialize(db_path); con = connect(db_path); dataset_id = register_demo(con)
    rng = np.random.default_rng(20261014); rows = []
    for subject in range(1, 7):
        pid = con.execute("INSERT INTO participant(dataset_id,subject_code,age,sex,analysis_included) VALUES (?,?,?,?,1)", (dataset_id, f"demo-{subject:02d}", 25 + subject, "U")).lastrowid
        sid = con.execute("INSERT INTO session(participant_id,session_label) VALUES (?,?)", (pid, "ses-01")).lastrowid
        rid = con.execute("INSERT INTO recording(session_id,modality,sampling_frequency,channel_count,source_uri) VALUES (?,?,?,?,?)", (sid, "EEG", 250.0, 19, "synthetic://demo")).lastrowid
        for level in range(1, 5):
            for epoch in range(3):
                t = np.arange(1000) / 250.0
                signal = rng.normal(0, 0.25, t.size) + (0.15 * level) * np.sin(2*np.pi*(6 + level)*t)
                feats = extract_features(signal, 250.0)
                epoch_id = (level - 1) * 3 + epoch
                rows.extend((rid, epoch_id, level, name, float(value)) for name, value in feats.items() if np.isfinite(value))
    run_id = con.execute("INSERT INTO processing_run(config_json,software_version,seed) VALUES (?,?,?)", (json.dumps({"mode":"synthetic-demo"}), "0.1.0", 20261014)).lastrowid
    con.executemany("INSERT INTO feature_record(recording_id,run_id,epoch_index,workload_level,feature_name,feature_value) VALUES (?,?,?,?,?,?)", [(r[0],run_id,r[1],r[2],r[3],r[4]) for r in rows])
    con.commit(); con.close()
    print(f"DEMO_OK database={db_path} features={len(rows)}")


def main() -> None:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("demo"); d.add_argument("--output", default="results/demo")
    i = sub.add_parser("init-db"); i.add_argument("path")
    args = p.parse_args()
    if args.command == "demo": run_demo(Path(args.output))
    else: initialize(args.path); print(f"DB_OK {args.path}")

if __name__ == "__main__": main()
