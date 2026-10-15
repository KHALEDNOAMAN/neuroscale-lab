-- Cohort-level feature summaries with a CTE and window ranking.
WITH participant_means AS (
    SELECT p.subject_code, f.feature_name, f.workload_level,
           AVG(f.feature_value) AS mean_value,
           COUNT(*) AS n_epochs
    FROM participant p
    JOIN session s ON s.participant_id = p.participant_id
    JOIN recording r ON r.session_id = s.session_id
    JOIN feature_record f ON f.recording_id = r.recording_id
    GROUP BY p.subject_code, f.feature_name, f.workload_level
), ranked AS (
    SELECT *, RANK() OVER (PARTITION BY feature_name, workload_level ORDER BY mean_value DESC) AS rank_in_level
    FROM participant_means
)
SELECT * FROM ranked ORDER BY feature_name, workload_level, rank_in_level;

-- QC report by recording and workload level.
SELECT r.recording_id, e.nback_level,
       COUNT(*) AS total_events,
       SUM(CASE WHEN q.decision = 'include' THEN 1 ELSE 0 END) AS included,
       SUM(CASE WHEN q.decision = 'exclude' THEN 1 ELSE 0 END) AS excluded
FROM recording r
JOIN event e ON e.recording_id = r.recording_id
LEFT JOIN qc_decision q ON q.event_id = e.event_id
GROUP BY r.recording_id, e.nback_level;

-- Provenance retrieval for a feature run.
SELECT pr.run_id, pr.config_json, a.path, a.bytes, a.sha256, a.role
FROM processing_run pr
JOIN artifact a ON a.run_id = pr.run_id
WHERE pr.run_id = ?
ORDER BY a.role, a.path;

-- Incremental entropy contrasts within participant.
SELECT subject_code, feature_name,
       MAX(CASE WHEN workload_level = 4 THEN mean_value END) -
       MAX(CASE WHEN workload_level = 1 THEN mean_value END) AS four_minus_one
FROM participant_workload_summary
WHERE feature_name IN ('permutation_entropy', 'mpe_scale_2', 'mpe_scale_4', 'mpe_scale_8')
GROUP BY subject_code, feature_name;
