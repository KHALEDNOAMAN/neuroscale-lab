from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QCDecision:
    include: bool
    reason: str
    level: int | None
    tutorial: bool
    dropout_overlap: bool


def classify_event(
    event: Any,
    dropout_onsets: Iterable[float],
    window_seconds: float,
    *,
    sampling_frequency: float | None = None,
    recording_samples: int | None = None,
) -> QCDecision:
    """Apply shared event QC, including recording boundaries when metadata is supplied.

    The optional pair must be passed by ingestion AND database integration, so
    an epoch cannot be marked included if its samples cannot be extracted.
    """
    if (sampling_frequency is None) != (recording_samples is None):
        raise ValueError("sampling_frequency and recording_samples must be passed together")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    if sampling_frequency is not None and (sampling_frequency <= 0 or recording_samples < 0):
        raise ValueError("sampling_frequency must be positive and recording_samples nonnegative")
    raw_level = event.get("nback_level")
    try:
        missing_level = raw_level is None or math.isnan(float(raw_level))
    except (TypeError, ValueError):
        missing_level = raw_level is None
    level = None if missing_level else int(raw_level)
    trial_type = str(event.get("trial_type", ""))
    tutorial = str(event.get("istutorial", "False")).lower() == "true"
    onset = float(event.get("onset", 0.0))
    dropout_overlap = any(onset <= float(dropout) < onset + window_seconds for dropout in dropout_onsets)
    if level not in {1, 2, 3, 4} or trial_type != f"{level}-back":
        return QCDecision(False, "not_a_labeled_task_event", level, tutorial, dropout_overlap)
    if tutorial:
        return QCDecision(False, "tutorial_event", level, tutorial, dropout_overlap)
    if dropout_overlap:
        return QCDecision(False, "dropout_overlap", level, tutorial, dropout_overlap)
    if sampling_frequency is not None:
        start = round(onset * sampling_frequency)
        stop = start + round(window_seconds * sampling_frequency)
        if start < 0 or stop > recording_samples:
            return QCDecision(False, "boundary_invalid", level, tutorial, False)
    return QCDecision(True, "eligible_task_event", level, tutorial, False)
