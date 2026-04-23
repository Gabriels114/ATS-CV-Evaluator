from datetime import date


def recency_factor(end_date: date | None, today: date) -> float:
    """
    Returns 1.0 for current/recent jobs, decays linearly to 0.3 at 10+ years ago.
    end_date=None means current role → always 1.0.
    """
    if end_date is None:
        return 1.0

    years_ago = (today - end_date).days / 365.25

    if years_ago <= 2:
        return 1.0
    if years_ago <= 5:
        # linear from 1.0 at 2y to 0.5 at 5y
        return 1.0 - (years_ago - 2) / 3 * 0.5
    if years_ago <= 10:
        # linear from 0.5 at 5y to 0.3 at 10y
        return 0.5 - (years_ago - 5) / 5 * 0.2

    return 0.3
