"""Extracts quantified metrics (money, percentages, multipliers, counts) from text."""

import re
from typing import Final

# Ordered from most specific to least specific to avoid partial overlaps.
_METRIC_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    # Dollar amounts: $2M, $500K, $1.5B, $200
    re.compile(r"\$\d+(?:\.\d+)?[KMBkmb]?\b"),
    # Percentages: 99.9%, 30%
    re.compile(r"\b\d+(?:\.\d+)?%"),
    # Multipliers: 10x, 3.5x, 2 times
    re.compile(r"\b\d+(?:\.\d+)?x\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?\s+times\b", re.IGNORECASE),
    # Large counts followed by a relevant domain noun.
    re.compile(
        r"\b\d{1,3}(?:,\d{3})+\s*(?:users?|requests?|records?|transactions?|events?|"
        r"downloads?|customers?|orders?|messages?|queries?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b\d{5,}\s*(?:users?|requests?|records?|transactions?|events?|"
        r"downloads?|customers?|orders?|messages?|queries?)\b",
        re.IGNORECASE,
    ),
    # Short-hand large numbers: 50K users, 2M requests
    re.compile(
        r"\b\d+(?:\.\d+)?[KMBkmb]\s*(?:users?|requests?|records?|transactions?|"
        r"events?|downloads?|customers?|orders?|messages?|queries?)\b",
        re.IGNORECASE,
    ),
    # Time savings: 3h, 12 hours, 5 days
    re.compile(r"\b\d+(?:\.\d+)?h\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?\s+(?:hours?|days?|weeks?|months?)\b", re.IGNORECASE),
)


def extract_metrics(text: str) -> list[str]:
    """
    Returns list of quantified metric strings found in text.
    Examples: ['$2M', '30%', '10x', '50K users', '99.9% uptime']
    """
    seen: set[str] = set()
    results: list[str] = []

    for pattern in _METRIC_PATTERNS:
        for match in pattern.finditer(text):
            metric = match.group(0).strip()
            if metric not in seen:
                seen = seen | {metric}
                results = [*results, metric]

    return results
