import os
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from ..config import MODEL_ID
from ..errors import ATSError, UnparseableDocumentError
from ..extraction import ClaudeClient, ExtractionMode, extract_cv, extract_jd
from ..parsers import parse_document
from ..reporting.json_export import to_dict
from ..scoring import score
from .ui import HTML_PAGE

app = FastAPI(title="ATS CV Evaluator", docs_url=None, redoc_url=None)

_ALLOWED_CV_EXTENSIONS = {".pdf", ".docx"}
_ALLOWED_JD_EXTENSIONS = {".txt", ".md"}
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the single-page web UI."""
    return HTMLResponse(HTML_PAGE)


@app.post("/evaluate")
async def evaluate(
    cv_file: Annotated[UploadFile, File(description="CV — PDF or DOCX")],
    jd_text: Annotated[str, Form(description="Job description text")] = "",
    jd_file: Annotated[UploadFile | None, File(description="JD — TXT or MD (optional)")] = None,
    mode: Annotated[str, Form(description="'local' or 'llm'")] = "local",
    api_key: Annotated[str, Form(description="Claude API key (LLM mode only)")] = "",
    model: Annotated[str, Form()] = MODEL_ID,
    no_cache: Annotated[bool, Form()] = False,
) -> JSONResponse:
    """Evaluate a CV against a job description and return a scored JSON report."""
    # ── Validate mode ─────────────────────────────────────────────────────────
    try:
        extraction_mode = ExtractionMode(mode.lower())
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid mode '{mode}'. Use 'local' or 'llm'.")

    # ── Validate CV file extension ────────────────────────────────────────────
    cv_suffix = Path(cv_file.filename or "").suffix.lower()
    if cv_suffix not in _ALLOWED_CV_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported CV format '{cv_suffix}'. Allowed: {', '.join(sorted(_ALLOWED_CV_EXTENSIONS))}",
        )

    # ── Validate JD file extension (if provided) ──────────────────────────────
    if jd_file and jd_file.filename:
        jd_suffix = Path(jd_file.filename).suffix.lower()
        if jd_suffix not in _ALLOWED_JD_EXTENSIONS:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported JD format '{jd_suffix}'. Allowed: {', '.join(sorted(_ALLOWED_JD_EXTENSIONS))}",
            )

    # ── Resolve extraction mode / build client ────────────────────────────────
    client: ClaudeClient | None = None
    if extraction_mode == ExtractionMode.LLM:
        resolved_key = api_key.strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not resolved_key:
            raise HTTPException(
                status_code=422,
                detail="LLM mode requires an API key. Enter it in the UI or set ANTHROPIC_API_KEY.",
            )
        client = ClaudeClient(api_key=resolved_key, model=model, use_cache=not no_cache)

    # ── Read and size-limit CV bytes ──────────────────────────────────────────
    cv_bytes = await cv_file.read(_MAX_UPLOAD_BYTES + 1)
    if len(cv_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="CV file exceeds 10 MB limit.")

    # ── Save CV to temp file; guarantee cleanup via outer try/finally ─────────
    with tempfile.NamedTemporaryFile(suffix=cv_suffix, delete=False) as tmp_cv:
        tmp_cv.write(cv_bytes)
        cv_path = Path(tmp_cv.name)

    try:
        # ── Resolve JD text ───────────────────────────────────────────────────
        if jd_file and jd_file.filename:
            jd_bytes = await jd_file.read(_MAX_UPLOAD_BYTES + 1)
            if len(jd_bytes) > _MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="JD file exceeds 10 MB limit.")

            with tempfile.NamedTemporaryFile(suffix=jd_suffix, delete=False) as tmp_jd:
                tmp_jd.write(jd_bytes)
                jd_path = Path(tmp_jd.name)
            try:
                jd_doc = parse_document(jd_path)
            except (UnparseableDocumentError, FileNotFoundError) as exc:
                raise HTTPException(status_code=422, detail=f"JD parse error: {exc}")
            finally:
                jd_path.unlink(missing_ok=True)
            resolved_jd_text = jd_doc.raw_text
        elif jd_text.strip():
            resolved_jd_text = jd_text.strip()
        else:
            raise HTTPException(status_code=422, detail="Provide a job description (text or file).")

        # ── Parse CV ──────────────────────────────────────────────────────────
        try:
            cv_doc = parse_document(cv_path)
        except (UnparseableDocumentError, FileNotFoundError) as exc:
            raise HTTPException(status_code=422, detail=f"CV parse error: {exc}")

    finally:
        # Guaranteed cleanup: runs even when JD validation or parse raises HTTPException
        cv_path.unlink(missing_ok=True)

    # ── Extract + Score ───────────────────────────────────────────────────────
    try:
        cv_data = extract_cv(cv_doc.raw_text, cv_doc.quality, client=client, mode=extraction_mode)
        jd_data = extract_jd(resolved_jd_text, client=client, mode=extraction_mode)
    except ATSError as exc:
        raise HTTPException(status_code=502, detail=f"Extraction error: {exc}")

    report = score(cv_data, jd_data)
    result = to_dict(report)
    result["extraction_mode"] = extraction_mode.value
    return JSONResponse(result)
