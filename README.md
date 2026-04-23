[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](#license)

# ATS-CV-Evaluator

A personal Applicant Tracking System (ATS) resume evaluator: CLI + web app powered by Claude API. Parse CVs and job descriptions, get detailed ATS compatibility scores with actionable feedback.

## What It Does

- **Parse multiple formats**: CVs (PDF, DOCX), Job Descriptions (TXT, MD)
- **Claude-powered extraction**: Uses Claude Sonnet 4.6 with tool-use structured extraction
- **Industry-weighted scoring**: Evaluates CVs across 7 dimensions:
  - Hard Skills (30%)
  - Experience (25%)
  - Education (15%)
  - Title Alignment (10%)
  - Achievements (10%)
  - Soft Skills (5%)
  - Formatting (5%)
- **Recency bias**: Recent experience weighted higher than older positions
- **Skill normalization**: Resolves aliases (js→javascript, k8s→kubernetes, postgres→postgresql, etc.)
- **Actionable feedback**: Missing keywords, ranked suggestions, improvement areas
- **Smart caching**: Caches Claude responses by SHA256 hash (optional, disable with `--no-cache`)
- **Two interfaces**: Terminal CLI with rich output + dark minimal web UI

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.11+ |
| AI | Anthropic Claude Sonnet 4.6 |
| Document Parsing | pdfplumber, python-docx |
| CLI | typer, rich |
| Web Server | FastAPI, uvicorn |
| Testing | pytest (72 tests, 82% coverage) |

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/gabriels114/ATS-CV-Evaluator.git
cd ATS-CV-Evaluator

# Install with dev & web extras
pip install -e ".[dev,web]"

# Set your API key
export ANTHROPIC_API_KEY=sk-...
# or create .env
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

### CLI Usage

```bash
# Basic evaluation
ats evaluate cv.pdf jd.txt

# Export as JSON
ats evaluate cv.pdf jd.txt --json report.json

# Use a different Claude model
ats evaluate cv.pdf jd.txt --model claude-opus-4-1

# Skip caching (fetch fresh evaluation)
ats evaluate cv.pdf jd.txt --no-cache

# Show version
ats version
```

### Web UI

```bash
# Start on default port (http://127.0.0.1:8000)
ats serve

# Or specify host and port
ats serve --host 0.0.0.0 --port 3000
```

Then open your browser and:
1. Drag & drop a CV (PDF or DOCX)
2. Paste the job description text
3. View animated score breakdown with missing keywords and suggestions

## Project Structure

```
src/ats_evaluator/
├── domain/              # Frozen dataclasses (immutable domain models)
│   ├── cv.py           # CV entity (skills, experience, education, etc.)
│   ├── job.py          # Job description entity (requirements, salary, etc.)
│   ├── scoring.py      # Score report entity
│   ├── feedback.py     # Feedback & suggestions
│   └── enums.py        # Skill levels, experience types, etc.
│
├── parsers/             # Repository pattern for document parsing
│   ├── base.py         # Parser interface
│   ├── pdf_parser.py   # PDF document parsing
│   ├── docx_parser.py  # DOCX document parsing
│   ├── text_parser.py  # TXT/MD document parsing
│   ├── parser_factory.py    # Dispatch to correct parser
│   └── format_quality.py    # Formatting analysis for scoring
│
├── extraction/          # Claude API integration with tool-use
│   ├── claude_client.py      # API client with caching
│   ├── cv_extractor.py       # Extract CV → structured data
│   ├── jd_extractor.py       # Extract JD → structured data
│   ├── response_validator.py # Validate Claude responses
│   └── prompts/              # Prompt engineering & JSON schemas
│       ├── cv_extraction.py
│       ├── jd_extraction.py
│       └── schemas.py        # Pydantic schemas for tool-use
│
├── scoring/             # Deterministic scoring engine
│   ├── engine.py        # Main scoring pipeline
│   ├── keyword_matcher.py    # Fuzzy skill matching
│   ├── recency.py       # Exponential decay for old experience
│   ├── weights.py       # Industry-standard dimension weights
│   └── dimensions/      # One file per scoring dimension
│       ├── hard_skills.py
│       ├── experience.py
│       ├── education.py
│       ├── title_alignment.py
│       ├── achievements.py
│       ├── soft_skills.py
│       └── formatting.py
│
├── feedback/            # Missing keywords & suggestions
│   ├── generator.py     # Generate actionable suggestions
│   └── missing_keywords.py   # Find gaps + severity tagging
│
├── reporting/           # Output formatting
│   ├── terminal.py      # Rich terminal rendering
│   ├── formatters.py    # Color coding, progress bars
│   └── json_export.py   # JSON serialization
│
├── web/                 # FastAPI web app
│   ├── app.py          # API endpoints
│   └── ui.py           # Single-page app (vanilla JS + CSS)
│
├── cli.py              # Typer CLI entry point
├── config.py           # Environment variable handling
├── errors.py           # Custom exceptions
└── __init__.py         # Package metadata
```

## Scoring Dimensions

Each dimension is scored 0-100, then weighted by industry ATS standards:

| Dimension | Weight | Evaluates |
|-----------|--------|-----------|
| Hard Skills | 30% | Required/preferred technical skills match |
| Experience | 25% | Role history, years, recency |
| Education | 15% | Degree, field, certifications |
| Title Alignment | 10% | Current/past titles vs. target role |
| Achievements | 10% | Quantified results, impact statements |
| Soft Skills | 5% | Communication, leadership, teamwork |
| Formatting | 5% | ATS readability, structure, parsing quality |

**Recency Bias**: Recent experience (< 2 years) weighted 100%, fading exponentially to ~30% for experience > 10 years old.

## Score Thresholds

| Score | Label | Interpretation |
|-------|-------|-----------------|
| 80+ | Strong Match | Passes most ATS filters, likely interview |
| 60-79 | Acceptable | Meets key requirements, competitive |
| 40-59 | At Risk | Missing important skills/experience |
| < 40 | Low Match | Likely auto-rejected by ATS systems |

## Web UI Features

- **Drag & drop uploads**: PDF or DOCX format
- **Live paste area**: Paste job description directly
- **Animated score bars**: Color-coded (green/yellow/red) with percentage
- **Score badge**: "Strong Match" / "Acceptable" / "At Risk" / "Low Match"
- **Missing keywords**: Severity tags (required=red, preferred=yellow)
- **Prioritized suggestions**: High/medium impact improvements
- **Dark minimal design**: No distractions, focus on results

## CLI Examples

### Evaluate a CV

```bash
$ ats evaluate my_cv.pdf senior_engineer_jd.txt

╭─────────────────────────────────────────────────╮
│          ATS Resume Evaluation Report            │
╰─────────────────────────────────────────────────╯

Overall Score:  78/100  ACCEPTABLE

Dimension Breakdown:
  Hard Skills:        92  ████████████████████ 92%
  Experience:         85  ██████████████████   85%
  Education:          75  █████████████████    75%
  Title Alignment:     70  ████████████████     70%
  Achievements:        68  ████████████████     68%
  Soft Skills:         60  ████████████         60%
  Formatting:          45  ██████████           45%

Missing Keywords (Required):
  • Kubernetes
  • PostgreSQL
  • Docker

Suggestions (High Priority):
  1. Add 2-3 quantified achievements (impact on revenue, perf, etc.)
  2. Improve CV formatting: use clear section headers
  3. Highlight cloud deployment experience (AWS/GCP)
```

### Export as JSON

```bash
$ ats evaluate cv.pdf jd.txt --json report.json
$ cat report.json
{
  "overall_score": 78,
  "label": "Acceptable",
  "dimensions": {
    "hard_skills": 92,
    "experience": 85,
    ...
  },
  "missing_keywords": [...],
  "suggestions": [...]
}
```

## Testing

The project includes 72 tests with 82% code coverage (pytest requirement):

```bash
# Run all tests
make test

# Or directly with pytest
pytest

# Run with coverage report
pytest --cov=ats_evaluator --cov-report=html

# Run specific test file
pytest tests/unit/scoring/test_engine.py

# Run with verbose output
pytest -vv
```

Test Structure:
- **Unit tests**: Individual functions, parsers, scoring dimensions
- **Integration tests**: Full scoring pipeline, Claude API mocking
- **E2E tests**: CLI command execution, file I/O

## Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY      # (Required) Your Claude API key
ANTHROPIC_MODEL        # (Optional) Override default model (default: claude-sonnet-4-6)
ATS_CACHE_DIR          # (Optional) Cache directory for Claude responses (default: ~/.cache/ats-evaluator)
```

### Supported File Formats

**CVs**: `.pdf`, `.docx`
**Job Descriptions**: `.txt`, `.md`

### Caching

Claude responses are cached by SHA256 hash of the document content. This:
- Reduces API costs (same CV against multiple JDs = 1 extraction)
- Speeds up re-evaluation
- Is disabled with `--no-cache` flag

Cache location: `~/.cache/ats-evaluator/`

## Development

### Setup

```bash
git clone https://github.com/gabriels114/ATS-CV-Evaluator.git
cd ATS-CV-Evaluator
pip install -e ".[dev,web]"
```

### Code Quality

```bash
make fmt           # Format code with Ruff
make lint          # Lint with Ruff
make test          # Run pytest
make check         # Lint + test
```

Configuration files:
- `pyproject.toml` - Build, pytest, coverage, mypy, ruff config
- `.ruff.toml` - Linter rules (E, F, I, UP, B, SIM)
- `Makefile` - Common development tasks

### Key Design Principles

1. **Immutability**: All domain models are frozen dataclasses. Data flows through immutable transformations.
2. **Separation of concerns**: Parsers, extractors, scorers, and reporters are isolated.
3. **Repository pattern**: Document parsing abstraction allows swapping implementations.
4. **Error handling**: Comprehensive exceptions with user-friendly error messages.
5. **Type safety**: Full mypy strict mode, Python 3.11+.

## Architecture

### Data Flow

```
CV/JD Files
    ↓
[Parsers] → Raw Text + Quality Metrics
    ↓
[Claude Extraction] → Structured Data (cached)
    ↓
[Scoring Engine] → Dimension Scores (0-100)
    ↓
[Feedback Generator] → Missing Keywords + Suggestions
    ↓
[Reporting] → Terminal/JSON/Web Output
```

### Parsing

- **PDF**: pdfplumber extracts text, preserves formatting quality
- **DOCX**: python-docx parses structure, detects tables and bullets
- **TXT/MD**: Plain text, minimal parsing

Formatting quality (5% of score) is assessed during parsing based on:
- Clarity of section headers
- Consistent bullet points
- Proper spacing and alignment
- ATS readability metrics

### Extraction

Claude is invoked with JSON schema tool-use to extract:

**From CV:**
- Contact info (name, email, phone)
- Professional summary
- Work experience (company, title, dates, achievements)
- Skills (technical, soft)
- Education (degree, institution, graduation date)
- Certifications
- Additional sections (projects, publications, volunteering)

**From JD:**
- Job title
- Required qualifications
- Preferred qualifications
- Hard skills list
- Soft skills list
- Experience requirements
- Education requirements
- Salary range (if present)

Responses are validated against Pydantic schemas before use.

### Scoring

Each dimension scorer receives structured CV and JD data, returns a score 0-100.

Example: Hard Skills dimension:
1. Extract CV skills + JD required/preferred skills
2. Fuzzy match with keyword normalization
3. Count matches (required weighted 2x preferred)
4. Apply penalties for missing critical skills
5. Return score

All dimensions combine using weighted average → **Overall Score (0-100)**.

## Performance

- **Single evaluation**: ~5-10 seconds (Claude API latency)
- **Cached evaluation**: <1 second
- **Web UI response**: <100ms (fast JSON response)

## Troubleshooting

### API Key Issues

```
Configuration error: ANTHROPIC_API_KEY not found
```

**Fix**: Set the environment variable or create `.env` file:
```bash
export ANTHROPIC_API_KEY=sk-...
# or
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

### Unparseable Document

```
Parse error: Could not extract text from PDF
```

**Fix**: Ensure PDF is not scanned/image-based (OCR not supported). Use searchable PDFs or convert with a tool like Adobe Acrobat.

### Web Dependencies Missing

```
Web dependencies not installed. Run: pip install 'ats-evaluator[web]'
```

**Fix**:
```bash
pip install -e ".[web]"
```

### Tests Failing

```bash
# Check your Python version
python --version  # Should be 3.11+

# Run with verbose output
pytest -vv

# Run specific failing test
pytest tests/unit/test_scoring.py::test_hard_skills -vv
```

## Screenshots

_Coming soon: Terminal output, web UI dark theme, score breakdown examples_

## License

MIT License - See LICENSE file for details.

## Contact

Gabriel Santiago - [@gabriels114](https://github.com/gabriels114)

---

**Built with**: Python · Claude API · FastAPI · Rich TUI
