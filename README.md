[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](#license)
[![Coverage](https://img.shields.io/badge/Coverage-83%25-brightgreen?style=flat-square)](#testing)

# ATS CV Evaluator

**Personal ATS resume evaluator with two extraction modes**: fast local (no API key) or accurate LLM-powered (Claude API). Evaluate how well a CV matches a job description with detailed scoring across 7 industry-weighted dimensions.

## What It Does

- **Two extraction modes**: Local (100% private, no API key) or LLM (Claude API for higher accuracy)
- **Parse multiple formats**: CVs (PDF, DOCX) and Job Descriptions (TXT, MD)
- **7-dimension scoring**: Hard Skills, Experience, Education, Title Alignment, Achievements, Soft Skills, Formatting
- **Local extraction stack**: Regex + 75+ skill taxonomy + optional spaCy NLP
- **5 industry improvements**:
  - Semantic embeddings (optional, `[semantic]` extra)
  - Placement weighting: skills in summary/skills sections score 1.3x higher
  - Skill recency decay: older skills weigh less
  - Contact validation with actionable suggestions
  - 40+ title variants per seniority level (bilingual ES/EN)
- **Web UI + CLI**: Choose your interface
- **Smart caching**: Cache Claude responses by content hash (LLM mode)

## Quick Start

```bash
# Install (no API key needed for local mode)
pip install ats-evaluator
source ats-env/bin/activate  # or your venv

# Evaluate with local extraction (default, instant)
ats evaluate cv.pdf jd.txt

# Or use Claude for higher accuracy (requires ANTHROPIC_API_KEY)
ats evaluate cv.pdf jd.txt --mode llm

# Start web UI
ats serve
```

## Installation

### Base Installation (Local Mode)

```bash
pip install ats-evaluator
```

### With Optional Features

| Extra | Purpose | Install |
|-------|---------|---------|
| `web` | FastAPI web UI | `pip install ats-evaluator[web]` |
| `semantic` | Sentence-transformers embeddings for skill matching | `pip install ats-evaluator[semantic]` |
| `local-nlp` | spaCy for enhanced local extraction | `pip install ats-evaluator[local-nlp]` |
| `fuzzy` | rapidfuzz for fuzzy skill matching | `pip install ats-evaluator[fuzzy]` |
| `dev` | Testing + linting (pytest, ruff, mypy) | `pip install ats-evaluator[dev]` |

### Install All Extras

```bash
pip install ats-evaluator[web,semantic,local-nlp,fuzzy,dev]
```

## Extraction Modes

### Local Mode (Default)

No API key required. Uses regex + skill taxonomy + optional spaCy.

```bash
ats evaluate cv.pdf jd.txt
```

**Pros:**
- Instant results (< 1 second)
- Completely private
- No API costs
- No rate limits

**Cons:**
- Less accurate than LLM
- Misses context and synonyms LLM would catch

**Stack:**
- Regex-based CV/JD parsing
- 75+ skill taxonomy with aliases (python3→python, k8s→kubernetes, etc.)
- Optional spaCy NLP (`pip install ats-evaluator[local-nlp]`)
- Contact extraction from standard CV sections
- Title matching against 40+ variants per level

### LLM Mode

Uses Claude API for structured extraction with tool-use.

```bash
export ANTHROPIC_API_KEY=sk-...
ats evaluate cv.pdf jd.txt --mode llm

# Or specify a different Claude model
ats evaluate cv.pdf jd.txt --mode llm --model claude-opus-4-1
```

**Pros:**
- Higher accuracy
- Understands context, synonyms, abbreviations
- Catches skills LLM would find

**Cons:**
- Requires ANTHROPIC_API_KEY
- API cost (~$0.01-0.05 per evaluation)
- Slower (~5-10 seconds)
- Rate limited by Anthropic

**Configuration:**
- Set `ANTHROPIC_API_KEY` environment variable or pass in web UI
- Default model: `claude-sonnet-4-6`
- Cache is enabled by default (same CV + model = cached)
- Disable cache with `--no-cache` flag

## Scoring Breakdown

Each dimension is scored 0-100 then weighted by industry ATS standards:

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Hard Skills | 30% | Technical skills match (required > preferred) |
| Experience | 25% | Years, relevance, recency |
| Education | 15% | Degree, field, certifications |
| Title Alignment | 10% | Current/past titles vs. job title |
| Achievements | 10% | Quantified results & impact statements |
| Soft Skills | 5% | Leadership, communication, teamwork |
| Formatting | 5% | ATS readability (headers, bullets, spacing) |

### Scoring Features

**Placement weighting**: Skills in Summary/Skills sections score 1.3x higher than in job descriptions.

**Recency decay**: Experience < 2 years weighted 100%, decaying exponentially to ~30% for experience > 10 years old.

## Score Interpretation

| Score | Label | Meaning |
|-------|-------|---------|
| 80+ | Strong Match | Passes most ATS filters, likely interview |
| 60-79 | Acceptable | Meets key requirements, competitive |
| 40-59 | At Risk | Missing important skills or experience |
| < 40 | Low Match | Likely auto-rejected by ATS systems |

## Web UI

Start the web server:

```bash
ats serve
# or specify host/port
ats serve --host 0.0.0.0 --port 3000
```

Open http://127.0.0.1:8000 in your browser.

**Features:**
- Drag & drop CV upload (PDF or DOCX)
- Paste or upload job description (TXT or MD)
- Toggle between Local and LLM modes
- Conditional API key field (only for LLM mode)
- Animated score breakdown with color coding
- Missing keywords by severity (required=red, preferred=yellow)
- Ranked improvement suggestions
- Dark minimal design

## CLI Commands

### Evaluate a CV

```bash
# Local mode (default)
ats evaluate cv.pdf jd.txt

# LLM mode
ats evaluate cv.pdf jd.txt --mode llm

# Export as JSON
ats evaluate cv.pdf jd.txt --json report.json

# Skip caching (LLM mode only)
ats evaluate cv.pdf jd.txt --mode llm --no-cache

# Use different Claude model
ats evaluate cv.pdf jd.txt --mode llm --model claude-opus-4-1

# Show version
ats version
```

### Start Web Server

```bash
ats serve                          # http://127.0.0.1:8000
ats serve --host 0.0.0.0 --port 3000
```

## Example Output

```
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
  Soft Skills:         60  ██████████           60%
  Formatting:          45  ██████████           45%

Missing Keywords (Required):
  • Kubernetes
  • PostgreSQL
  • Docker

Suggestions (High Priority):
  1. Add 2-3 quantified achievements (revenue impact, performance metrics, etc.)
  2. Improve CV formatting: use clear section headers and consistent bullets
  3. Highlight cloud deployment experience (AWS/GCP)
```

## Architecture

### Project Structure

```
src/ats_evaluator/
├── domain/              # Frozen dataclasses (immutable models)
│   ├── cv.py           # CV entity
│   ├── job.py          # Job description entity
│   ├── scoring.py      # Score report
│   ├── feedback.py     # Suggestions & missing keywords
│   └── enums.py        # Skill levels, etc.
│
├── parsers/             # Document parsing (PDF, DOCX, TXT, MD)
│   ├── base.py         # Parser interface
│   ├── pdf_parser.py   # PDF extraction
│   ├── docx_parser.py  # DOCX extraction
│   ├── text_parser.py  # TXT/MD parsing
│   ├── parser_factory.py    # Dispatch to correct parser
│   └── format_quality.py    # ATS readability scoring
│
├── extraction/          # CV & JD extraction
│   ├── local/          # Regex + taxonomy (no API)
│   │   ├── cv_extractor.py
│   │   ├── jd_extractor.py
│   │   └── skills_db.py    # 75+ skill taxonomy
│   ├── llm/            # Claude API extraction
│   │   ├── cv_extractor.py
│   │   └── jd_extractor.py
│   ├── claude_client.py     # API client with caching
│   ├── mode.py         # ExtractionMode enum (LOCAL | LLM)
│   └── prompts/        # Prompts and Pydantic schemas
│
├── scoring/             # Scoring engine
│   ├── engine.py        # Main pipeline
│   ├── weights.py       # Dimension weights
│   ├── keyword_matcher.py    # Fuzzy skill matching
│   ├── semantic_matcher.py   # Optional: embeddings
│   ├── recency.py       # Skill age decay
│   └── dimensions/      # One file per dimension
│       ├── hard_skills.py
│       ├── experience.py
│       ├── education.py
│       ├── title_alignment.py
│       ├── achievements.py
│       ├── soft_skills.py
│       └── formatting.py
│
├── feedback/            # Suggestions engine
│   ├── generator.py     # Generate suggestions
│   └── missing_keywords.py   # Find gaps + severity
│
├── reporting/           # Output formatting
│   ├── terminal.py      # Rich terminal rendering
│   ├── json_export.py   # JSON serialization
│   └── formatters.py    # Color coding, progress bars
│
├── web/                 # FastAPI web app
│   ├── app.py          # API endpoints
│   └── ui.py           # Single-page HTML + CSS + JS
│
├── cli.py              # Typer CLI entry point
├── config.py           # Environment variable handling
├── errors.py           # Custom exceptions
└── __init__.py         # Package metadata
```

### Data Flow

```
CV/JD Files
    ↓
[Parsers] → Raw text + formatting quality
    ↓
[Extractors] → Structured data (cached if LLM)
    ↓
[Scoring Engine] → Dimension scores 0-100
    ↓
[Feedback Generator] → Missing keywords + suggestions
    ↓
[Reporting] → Terminal/JSON/Web output
```

## Testing

The project includes 83% code coverage with pytest:

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=ats_evaluator --cov-report=html

# Run specific test file
pytest tests/unit/scoring/test_engine.py

# Verbose output
pytest -vv

# Run with make
make test
```

Test structure:
- **Unit tests**: Individual functions, parsers, scorers
- **Integration tests**: Full pipeline, Claude API mocking
- **E2E tests**: CLI commands, file I/O

Requirement: 80%+ coverage enforced in `pyproject.toml`.

## Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY      # (Required for LLM mode) Your Claude API key
ANTHROPIC_MODEL        # (Optional) Override default model (default: claude-sonnet-4-6)
ATS_CACHE_DIR          # (Optional) Cache directory (default: ~/.cache/ats-evaluator)
```

### File Formats

**CVs**: `.pdf`, `.docx`  
**Job Descriptions**: `.txt`, `.md`

### Caching (LLM Mode)

Claude responses are cached by SHA256 hash of document content:
- Same CV + model = cached response (< 100ms)
- Reduces API costs
- Disable with `--no-cache` flag

Cache location: `~/.cache/ats-evaluator/`

## Development

### Setup

```bash
git clone https://github.com/gabriels114/ATS-CV-Evaluator.git
cd ATS-CV-Evaluator
python -m venv ats-env
source ats-env/bin/activate  # Windows: ats-env\Scripts\activate
pip install -e ".[dev,web]"
```

### Code Quality

```bash
make lint        # Ruff linting
make fmt         # Format with Ruff
make test        # Pytest with coverage
make check       # Lint + test
```

### Design Principles

1. **Immutability**: All domain models are frozen dataclasses. Immutable data flows through transformations.
2. **Separation of concerns**: Parsers, extractors, scorers, reporters are isolated.
3. **Repository pattern**: Document parsing abstraction allows swapping implementations.
4. **Error handling**: Comprehensive exceptions with user-friendly messages.
5. **Type safety**: Full mypy strict mode, Python 3.11+.

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

Set the environment variable or create `.env` file:

```bash
export ANTHROPIC_API_KEY=sk-...
# or
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

### "Could not extract text from PDF"

Ensure the PDF is searchable (not scanned/image-based). Convert with Adobe Acrobat or similar OCR tool.

### "Web dependencies not installed"

```bash
pip install ats-evaluator[web]
```

### Tests failing

```bash
# Check Python version (must be 3.11+)
python --version

# Run with verbose output
pytest -vv

# Run specific test
pytest tests/unit/scoring/test_engine.py::test_hard_skills -vv
```

## Performance

- **Local mode**: < 1 second per evaluation
- **LLM mode (fresh)**: 5-10 seconds (Claude API latency)
- **LLM mode (cached)**: < 100ms
- **Web UI response**: < 100ms (after extraction)

## License

MIT License — See LICENSE file for details.

## Contact

Gabriel Santiago — [@gabriels114](https://github.com/gabriels114)

---

**Built with**: Python · Claude API · FastAPI · Rich TUI
