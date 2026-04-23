import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from ..config import MODEL_ID, get_api_key
from ..errors import ATSError, ConfigurationError, UnparseableDocumentError
from ..extraction import ClaudeClient, extract_cv, extract_jd
from ..parsers import parse_document
from ..reporting.json_export import to_dict
from ..scoring import score
from .ui import HTML_PAGE

app = FastAPI(title="ATS CV Evaluator", docs_url=None, redoc_url=None)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(HTML_PAGE)


@app.post("/evaluate")
async def evaluate(
    cv_file: Annotated[UploadFile, File(description="CV — PDF or DOCX")],
    jd_text: Annotated[str, Form(description="Job description text")] = "",
    jd_file: Annotated[UploadFile | None, File(description="JD — TXT or MD (optional)")] = None,
    model: Annotated[str, Form()] = MODEL_ID,
    no_cache: Annotated[bool, Form()] = False,
) -> JSONResponse:
    try:
        api_key = get_api_key()
    except ConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # ── Save CV to temp file ──────────────────────────────────────────────────
    cv_suffix = Path(cv_file.filename or "cv.pdf").suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=cv_suffix, delete=False) as tmp_cv:
        tmp_cv.write(await cv_file.read())
        cv_path = Path(tmp_cv.name)

    # ── Resolve JD text ───────────────────────────────────────────────────────
    if jd_file and jd_file.filename:
        jd_suffix = Path(jd_file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=jd_suffix, delete=False) as tmp_jd:
            tmp_jd.write(await jd_file.read())
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

    # ── Parse CV ──────────────────────────────────────────────────────────────
    try:
        cv_doc = parse_document(cv_path)
    except (UnparseableDocumentError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=f"CV parse error: {exc}")
    finally:
        cv_path.unlink(missing_ok=True)

    # ── Extract + Score ───────────────────────────────────────────────────────
    client = ClaudeClient(api_key=api_key, model=model, use_cache=not no_cache)
    try:
        cv_data = extract_cv(cv_doc.raw_text, cv_doc.quality, client)
        jd_data = extract_jd(resolved_jd_text, client)
    except ATSError as exc:
        raise HTTPException(status_code=502, detail=f"Extraction error: {exc}")

    report = score(cv_data, jd_data)
    return JSONResponse(to_dict(report))
