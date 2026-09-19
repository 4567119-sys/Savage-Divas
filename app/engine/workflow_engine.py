from typing import Optional, Tuple

from app.config import settings
from app.engine.requirement_checker import check_requirements
from app.models.case import Case


def determine_next_stage(
    case: Case,
    confidence: Optional[float] = None,
    flagged_anomalies: Optional[list[str]] = None,
) -> Tuple[str, str, Optional[str]]:
    """
    Determine the next workflow stage for a case.

    Returns:
        (next_stage, status, trigger_reason)
    """

    anomalies = flagged_anomalies or []

    # AI has identified something that needs human attention.
    if anomalies:
        return (
            "ADVISER_REVIEW",
            "ADVISER_INTERVENTION",
            "ANOMALY_DETECTED",
        )

    # Low confidence requires human review.
    if confidence is not None and confidence < settings.AI_CONFIDENCE_THRESHOLD:
        return (
            "ADVISER_REVIEW",
            "ADVISER_INTERVENTION",
            "LOW_AI_CONFIDENCE",
        )

    # Check whether all case requirements have been fulfilled.
    all_fulfilled, missing_requirements = check_requirements(case)

    # Missing requirements require human attention.
    if not all_fulfilled:
        return (
            "ADVISER_REVIEW",
            "ADVISER_INTERVENTION",
            "MISSING_CRITICAL_DOC",
        )

    # All checks passed.
    return (
        "ADVISER_REVIEW",
        "IN_PROGRESS",
        None,
    )