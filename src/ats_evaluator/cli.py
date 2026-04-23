from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .config import get_api_key
from .errors import ATSError, ConfigurationError, UnparseableDocumentError
from .extraction import ClaudeClient, ExtractionMode, extract_cv, extract_jd
from .parsers import parse_document
from .reporting import render_report, to_json
from .scoring import score

app = typer.Typer(
    name="ats",
    help="Personal ATS resume evaluator — local or LLM-powered.",
    add_completion=False,
)
console = Console()


@app.command()
def evaluate(
    cv_path: Path = typer.Argument(..., help="Path to your CV (PDF or DOCX)", metavar="CV"),
    jd_path: Path = typer.Argument(..., help="Path to the job description (TXT or MD)", metavar="JD"),
    mode: ExtractionMode = typer.Option(
        ExtractionMode.LOCAL, "--mode", "-M",
        help="'local' = no API key needed · 'llm' = Claude for higher accuracy",
    ),
    json_out: Optional[Path] = typer.Option(None, "--json", "-j", help="Export report as JSON"),
    model: str = typer.Option("claude-sonnet-4-6", "--model", "-m", help="Claude model (LLM mode only)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip cached Claude responses (LLM mode only)"),
) -> None:
    """Evaluate a CV against a job description and produce an ATS score report."""
    client: ClaudeClient | None = None

    if mode == ExtractionMode.LLM:
        try:
            api_key = get_api_key()
        except ConfigurationError as exc:
            console.print(f"[red]Configuration error:[/red] {exc}")
            raise typer.Exit(3)
        client = ClaudeClient(api_key=api_key, model=model, use_cache=not no_cache)

    try:
        with console.status("[bold cyan]Parsing CV..."):
            cv_doc = parse_document(cv_path)
        with console.status("[bold cyan]Parsing Job Description..."):
            jd_doc = parse_document(jd_path)
    except FileNotFoundError as exc:
        console.print(f"[red]File not found:[/red] {exc}")
        raise typer.Exit(2)
    except UnparseableDocumentError as exc:
        console.print(f"[red]Parse error:[/red] {exc}")
        raise typer.Exit(2)

    mode_label = "[green]local[/green]" if mode == ExtractionMode.LOCAL else "[magenta]LLM (Claude)[/magenta]"
    try:
        with console.status(f"[bold cyan]Extracting CV data ({mode_label})..."):
            cv_data = extract_cv(cv_doc.raw_text, cv_doc.quality, client=client, mode=mode)
        with console.status(f"[bold cyan]Extracting JD requirements ({mode_label})..."):
            jd_data = extract_jd(jd_doc.raw_text, client=client, mode=mode)
    except ATSError as exc:
        console.print(f"[red]Extraction error:[/red] {exc}")
        raise typer.Exit(1)

    with console.status("[bold cyan]Scoring..."):
        report = score(cv_data, jd_data)

    render_report(report, console)

    if json_out:
        json_out.write_text(to_json(report), encoding="utf-8")
        console.print(f"[dim]JSON report saved to {json_out}[/dim]")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to listen on"),
) -> None:
    """Start the web UI (requires: pip install 'ats-evaluator[web]')."""
    try:
        import uvicorn
    except ImportError:
        console.print("[red]Web dependencies not installed.[/red] Run: pip install 'ats-evaluator[web]'")
        raise typer.Exit(1)

    console.print(f"[bold cyan]ATS Web UI[/bold cyan] → http://{host}:{port}")
    uvicorn.run("ats_evaluator.web.app:app", host=host, port=port, reload=False)


@app.command()
def version() -> None:
    """Show the version and available extraction modes."""
    console.print(f"ats-evaluator {__version__}")
    console.print("[dim]Modes: local (default, no API key) · llm (Claude API)[/dim]")


if __name__ == "__main__":
    app()
