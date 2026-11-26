"""Deterministic helper tools for consistent, auditable ratings and dates."""

import datetime as _dt

from mistralai import agents

RATING_ORDER = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}


@agents.tool
def score_risk(likelihood: int, impact: int) -> dict:
    """Score a project risk on a 5x5 likelihood x impact matrix.

    Args:
        likelihood: 1 (rare) to 5 (almost certain).
        impact: 1 (negligible) to 5 (severe: contract validity, life safety,
            major cost >5% of contract value, or critical-path delay).

    Returns:
        dict with the risk score, rating (Low/Medium/High/Critical), and the
        banding rationale.
    """
    if not 1 <= likelihood <= 5 or not 1 <= impact <= 5:
        raise agents.ToolError("likelihood and impact must both be integers from 1 to 5.")
    score = likelihood * impact
    if score >= 20:
        rating = "Critical"
    elif score >= 12:
        rating = "High"
    elif score >= 6:
        rating = "Medium"
    else:
        rating = "Low"
    return {
        "score": score,
        "rating": rating,
        "rationale": (
            f"likelihood {likelihood} x impact {impact} = {score}; "
            "Critical >=20, High 12-19, Medium 6-11, Low <6"
        ),
    }


@agents.tool
def days_until(due_date: str, reference_date: str | None = None) -> dict:
    """Days remaining until (or overdue past) an ISO date (YYYY-MM-DD).

    Args:
        due_date: deadline as an ISO date, e.g. "2025-08-15".
        reference_date: optional ISO date to compare against; defaults to today.

    Returns:
        dict with days_remaining (negative when overdue) and status
        ("overdue", "due today", "due soon" for <=7 days, or "scheduled").
    """
    try:
        due = _dt.date.fromisoformat(due_date.strip())
    except ValueError as exc:
        raise agents.ToolError(f"due_date must be ISO YYYY-MM-DD, got {due_date!r}") from exc
    if reference_date is None:
        today = agents.now().date()
    else:
        try:
            today = _dt.date.fromisoformat(reference_date.strip())
        except ValueError as exc:
            raise agents.ToolError(
                f"reference_date must be ISO YYYY-MM-DD, got {reference_date!r}"
            ) from exc
    remaining = (due - today).days
    if remaining < 0:
        status = "overdue"
    elif remaining == 0:
        status = "due today"
    elif remaining <= 7:
        status = "due soon"
    else:
        status = "scheduled"
    return {"days_remaining": remaining, "status": status}
