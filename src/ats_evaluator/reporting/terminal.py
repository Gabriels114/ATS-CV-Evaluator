from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..domain.feedback import Priority, Severity
from ..domain.scoring import ScoreReport
from .formatters import DIM, score_bar, score_label, score_style

_PRIORITY_ICONS = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}
_SEVERITY_ICONS = {Severity.REQUIRED: "[red]✗[/red]", Severity.PREFERRED: "[yellow]~[/yellow]"}


def render_report(report: ScoreReport, console: Console) -> None:
    console.print()
    console.rule("[bold]ATS CV Evaluator Report[/bold]")
    console.print(f"  CV:  {report.cv_summary}", style=DIM)
    console.print(f"  JD:  {report.jd_summary}", style=DIM)
    console.print(f"  Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')}  |  Scoring v{report.scoring_version}", style=DIM)
    console.print()

    # Total score
    style = score_style(report.total_score)
    label = score_label(report.total_score)
    total_text = Text(f"  {report.total_score:.1f} / 100  {label}", style=style)
    console.print(Panel(total_text, title="[bold]Total ATS Score[/bold]", expand=False))
    console.print()

    # Dimension breakdown table
    table = Table(title="Score Breakdown", show_header=True, header_style="bold cyan")
    table.add_column("Dimension", style="bold", min_width=18)
    table.add_column("Score", justify="right", min_width=8)
    table.add_column("Weight", justify="right", min_width=7)
    table.add_column("Weighted", justify="right", min_width=9)
    table.add_column("Bar", min_width=32)

    for dim in sorted(report.dimensions, key=lambda d: d.raw_score):
        bar = score_bar(dim.raw_score)
        table.add_row(
            dim.name.replace("_", " ").title(),
            f"{dim.raw_score:.1f}",
            f"{dim.weight * 100:.0f}%",
            f"{dim.weighted_score:.1f}",
            f"[{_bar_color(dim.raw_score)}]{bar}[/]",
        )

    console.print(table)
    console.print()

    # Missing keywords
    if report.missing_keywords:
        required = [m for m in report.missing_keywords if m.severity == Severity.REQUIRED]
        preferred = [m for m in report.missing_keywords if m.severity == Severity.PREFERRED]

        missing_lines: list[str] = []
        for m in required[:10]:
            missing_lines.append(f"  {_SEVERITY_ICONS[m.severity]} {m.keyword}")
        for m in preferred[:5]:
            missing_lines.append(f"  {_SEVERITY_ICONS[m.severity]} {m.keyword}")

        console.print(Panel(
            "\n".join(missing_lines) or "None",
            title="[bold]Missing Keywords[/bold]",
        ))
        console.print()

    # Suggestions
    if report.suggestions:
        high = [s for s in report.suggestions if s.priority == Priority.HIGH]
        medium = [s for s in report.suggestions if s.priority == Priority.MEDIUM]
        shown = (high + medium)[:6]

        suggestion_lines = [
            f"  {_PRIORITY_ICONS[s.priority]} [{s.dimension}] {s.message}"
            for s in shown
        ]
        console.print(Panel(
            "\n\n".join(suggestion_lines),
            title="[bold]Actionable Suggestions[/bold]",
        ))
        console.print()


def _bar_color(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"
