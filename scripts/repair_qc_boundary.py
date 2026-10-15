"""One-time verified correction for the Phase 3 sub-011 boundary QC mismatch.

Uses SQLite's online backup API; requires no raw EEG acquisition files.
Does not modify model results or extracted features.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

EVENT_ID = 11986
SUBJECT = "sub-011"
EXPECTED_ONSET = 1076.884421


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    path = args.database.resolve()
    if not path.is_file():
        parser.error(f"database not found: {path}")

    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    q = """SELECT q.qc_id, q.decision, q.reason, e.onset_seconds,
                  p.subject_code, e.recording_id, e.event_id
           FROM qc_decision q JOIN event e ON e.event_id=q.event_id
           JOIN recording r ON r.recording_id=e.recording_id
           JOIN session s ON s.session_id=r.session_id
           JOIN participant p ON p.participant_id=s.participant_id
           WHERE e.event_id=?"""
    row = con.execute(q, (EVENT_ID,)).fetchone()
    if not row:
        raise RuntimeError("Expected Phase 3 event is not in the database; no changes made")
    qc_id, decision, reason, onset, subject, recording_id, event_id = row
    if subject != SUBJECT or abs(onset - EXPECTED_ONSET) > 1e-6:
        raise RuntimeError(f"Unexpected event identity: {row!r}; no changes made")
    if decision == "exclude" and reason == "boundary_invalid":
        print("QC_ALREADY_FIXED; no database changes needed")
        return
    if decision != "include" or reason != "eligible_task_event":
        raise RuntimeError(f"Unexpected QC state: {decision}, {reason}; no changes made")
    min_event = con.execute(
        "SELECT MIN(event_id) FROM event WHERE recording_id=?", (recording_id,)
    ).fetchone()[0]
    epoch_index = event_id - min_event
    count = con.execute(
        "SELECT COUNT(*) FROM feature_record WHERE recording_id=? AND epoch_index=?",
        (recording_id, epoch_index),
    ).fetchone()[0]
    if count:
        raise RuntimeError(f"Event has {count} feature records; refusing to exclude")
    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise RuntimeError("Database integrity_check failed; refusing migration")

    backup = path.with_name(path.stem + ".before-qc-fix." + datetime.now().strftime("%Y%m%d-%H%M%S") + path.suffix)
    with sqlite3.connect(backup) as backup_con:
        con.backup(backup_con)
    print(f"BACKUP_CREATED {backup}")
    with con:
        old_json = con.execute(
            "SELECT metric_json FROM qc_decision WHERE qc_id=?", (qc_id,)
        ).fetchone()[0]
        metrics = json.loads(old_json)
        metrics["boundary_invalid"] = True
        cur = con.execute(
            "UPDATE qc_decision SET decision='exclude',reason='boundary_invalid',metric_json=? "
            "WHERE qc_id=? AND decision='include' AND reason='eligible_task_event'",
            (json.dumps(metrics, sort_keys=True), qc_id),
        )
        if cur.rowcount != 1:
            raise RuntimeError("Expected exactly one QC record to update")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Foreign key violations; rolling back")
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Integrity violation; rolling back")
    print(f"QC_FIXED subject={subject} event={event_id} epoch_index={epoch_index}")
    con.close()


if __name__ == "__main__":
    main()
