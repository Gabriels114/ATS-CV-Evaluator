from rich.style import Style

GREEN = Style(color="green", bold=True)
YELLOW = Style(color="yellow", bold=True)
RED = Style(color="red", bold=True)
DIM = Style(dim=True)


def score_style(score: float) -> Style:
    if score >= 80:
        return GREEN
    if score >= 60:
        return YELLOW
    return RED


def score_bar(score: float, width: int = 30) -> str:
    filled = int(round(score / 100 * width))
    return "█" * filled + "░" * (width - filled)


def score_label(score: float) -> str:
    if score >= 80:
        return "STRONG MATCH"
    if score >= 60:
        return "ACCEPTABLE"
    if score >= 40:
        return "AT RISK"
    return "LOW MATCH"
