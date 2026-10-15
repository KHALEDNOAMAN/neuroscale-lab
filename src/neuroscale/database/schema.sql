PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dataset (
    dataset_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    version TEXT NOT NULL,
    doi TEXT,
    license TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS participant (
    participant_id INTEGER PRIMARY KEY,
    dataset_id INTEGER NOT NULL REFERENCES dataset(dataset_id) ON DELETE CASCADE,
    subject_code TEXT NOT NULL,
    age REAL,
    sex TEXT,
    analysis_included INTEGER NOT NULL CHECK (analysis_included IN (0,1)),
    UNIQUE(dataset_id, subject_code)
);
CREATE TABLE IF NOT EXISTS session (
    session_id INTEGER PRIMARY KEY,
    participant_id INTEGER NOT NULL REFERENCES participant(participant_id) ON DELETE CASCADE,
    session_label TEXT NOT NULL,
    UNIQUE(participant_id, session_label)
);
CREATE TABLE IF NOT EXISTS recording (
    recording_id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    modality TEXT NOT NULL,
    sampling_frequency REAL NOT NULL CHECK (sampling_frequency > 0),
    channel_count INTEGER NOT NULL CHECK (channel_count > 0),
    reference TEXT,
    source_uri TEXT NOT NULL,
    sha256 TEXT,
    UNIQUE(session_id, modality, source_uri)
);
CREATE TABLE IF NOT EXISTS channel (
    channel_id INTEGER PRIMARY KEY,
    recording_id INTEGER NOT NULL REFERENCES recording(recording_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    channel_type TEXT NOT NULL DEFAULT 'EEG',
    UNIQUE(recording_id, name)
);
CREATE TABLE IF NOT EXISTS event (
    event_id INTEGER PRIMARY KEY,
    recording_id INTEGER NOT NULL REFERENCES recording(recording_id) ON DELETE CASCADE,
    onset_seconds REAL NOT NULL CHECK (onset_seconds >= 0),
    duration_seconds REAL,
    trial_type TEXT NOT NULL,
    nback_level INTEGER CHECK (nback_level BETWEEN 1 AND 4),
    is_tutorial INTEGER NOT NULL DEFAULT 0 CHECK (is_tutorial IN (0,1)),
    dropped_samples INTEGER NOT NULL DEFAULT 0 CHECK (dropped_samples >= 0),
    response_accuracy INTEGER CHECK (response_accuracy IN (0,1))
);
CREATE TABLE IF NOT EXISTS processing_run (
    run_id INTEGER PRIMARY KEY,
    config_json TEXT NOT NULL,
    software_version TEXT NOT NULL,
    seed INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS artifact (
    artifact_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES processing_run(run_id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    bytes INTEGER NOT NULL CHECK (bytes >= 0),
    sha256 TEXT NOT NULL,
    role TEXT NOT NULL,
    UNIQUE(run_id, path)
);
CREATE TABLE IF NOT EXISTS qc_decision (
    qc_id INTEGER PRIMARY KEY,
    recording_id INTEGER NOT NULL REFERENCES recording(recording_id) ON DELETE CASCADE,
    event_id INTEGER REFERENCES event(event_id) ON DELETE CASCADE,
    decision TEXT NOT NULL CHECK (decision IN ('include','exclude','flag')),
    reason TEXT NOT NULL,
    metric_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS feature_record (
    feature_id INTEGER PRIMARY KEY,
    recording_id INTEGER NOT NULL REFERENCES recording(recording_id) ON DELETE CASCADE,
    channel_id INTEGER REFERENCES channel(channel_id) ON DELETE RESTRICT,
    run_id INTEGER NOT NULL REFERENCES processing_run(run_id) ON DELETE RESTRICT,
    epoch_index INTEGER NOT NULL,
    workload_level INTEGER NOT NULL CHECK (workload_level BETWEEN 1 AND 4),
    feature_name TEXT NOT NULL,
    feature_value REAL NOT NULL,
    UNIQUE(recording_id, run_id, epoch_index, feature_name)
);
CREATE TABLE IF NOT EXISTS model_evaluation (
    evaluation_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES processing_run(run_id) ON DELETE CASCADE,
    feature_group TEXT NOT NULL,
    model_name TEXT NOT NULL,
    fold_id INTEGER NOT NULL,
    test_subjects_json TEXT NOT NULL,
    balanced_accuracy REAL NOT NULL,
    macro_f1 REAL NOT NULL,
    confusion_matrix_json TEXT NOT NULL,
    UNIQUE(run_id, feature_group, model_name, fold_id)
);

CREATE INDEX IF NOT EXISTS ix_event_level ON event(nback_level, trial_type);
CREATE INDEX IF NOT EXISTS ix_qc_recording ON qc_decision(recording_id, decision);
CREATE INDEX IF NOT EXISTS ix_feature_lookup ON feature_record(workload_level, feature_name);
CREATE INDEX IF NOT EXISTS ix_eval_group ON model_evaluation(feature_group, model_name);

CREATE VIEW IF NOT EXISTS participant_workload_summary AS
SELECT p.subject_code, f.workload_level, f.feature_name,
       AVG(f.feature_value) AS mean_value, COUNT(*) AS n_epochs
FROM participant p
JOIN session s ON s.participant_id = p.participant_id
JOIN recording r ON r.session_id = s.session_id
JOIN feature_record f ON f.recording_id = r.recording_id
GROUP BY p.subject_code, f.workload_level, f.feature_name;

CREATE VIEW IF NOT EXISTS cohort_qc_summary AS
SELECT p.subject_code, r.recording_id,
       SUM(CASE WHEN q.decision = 'include' THEN 1 ELSE 0 END) AS included_events,
       SUM(CASE WHEN q.decision = 'exclude' THEN 1 ELSE 0 END) AS excluded_events,
       SUM(CASE WHEN q.decision = 'flag' THEN 1 ELSE 0 END) AS flagged_events
FROM participant p
JOIN session s ON s.participant_id = p.participant_id
JOIN recording r ON r.session_id = s.session_id
LEFT JOIN qc_decision q ON q.recording_id = r.recording_id
GROUP BY p.subject_code, r.recording_id;
