HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ATS CV Evaluator</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #0f1117;
    --surface:  #1a1d27;
    --border:   #2a2d3a;
    --text:     #e4e6f0;
    --muted:    #6b7280;
    --accent:   #6366f1;
    --green:    #22c55e;
    --yellow:   #eab308;
    --red:      #ef4444;
    --radius:   10px;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 14px;
    min-height: 100vh;
    padding: 40px 20px;
  }

  .container { max-width: 860px; margin: 0 auto; }

  header { margin-bottom: 36px; }
  header h1 { font-size: 22px; font-weight: 600; letter-spacing: -0.3px; }
  header p  { color: var(--muted); margin-top: 4px; font-size: 13px; }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 16px;
  }

  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } }

  label {
    display: block;
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
    margin-bottom: 6px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  .drop-zone {
    border: 1.5px dashed var(--border);
    border-radius: 8px;
    padding: 28px 16px;
    text-align: center;
    cursor: pointer;
    transition: border-color .15s, background .15s;
    position: relative;
  }
  .drop-zone:hover, .drop-zone.dragover {
    border-color: var(--accent);
    background: rgba(99,102,241,.05);
  }
  .drop-zone input[type=file] {
    position: absolute; inset: 0; opacity: 0;
    cursor: pointer; width: 100%; height: 100%;
  }
  .drop-zone .icon     { font-size: 24px; margin-bottom: 6px; }
  .drop-zone .hint     { font-size: 12px; color: var(--muted); }
  .drop-zone .filename { font-size: 12px; color: var(--accent); margin-top: 4px; font-weight: 500; }

  textarea {
    width: 100%;
    background: var(--bg);
    border: 1.5px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 13px;
    font-family: inherit;
    padding: 12px;
    resize: vertical;
    height: 140px;
    outline: none;
    transition: border-color .15s;
  }
  textarea:focus { border-color: var(--accent); }
  textarea::placeholder { color: var(--muted); }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity .15s;
    width: 100%;
    justify-content: center;
    margin-top: 16px;
  }
  .btn:hover { opacity: .85; }
  .btn:disabled { opacity: .4; cursor: default; }

  .spinner {
    width: 16px; height: 16px;
    border: 2px solid rgba(255,255,255,.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin .6s linear infinite;
    display: none;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .score-hero {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 24px;
  }
  .score-circle {
    width: 90px; height: 90px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 3px solid;
    flex-shrink: 0;
  }
  .score-circle .num   { font-size: 26px; font-weight: 700; line-height: 1; }
  .score-circle .denom { font-size: 11px; color: var(--muted); }
  .score-meta h2 { font-size: 18px; font-weight: 600; }
  .score-meta p  { font-size: 13px; color: var(--muted); margin-top: 4px; }

  .green  { color: var(--green);  border-color: var(--green); }
  .yellow { color: var(--yellow); border-color: var(--yellow); }
  .red    { color: var(--red);    border-color: var(--red); }
  .bg-green  { background: rgba(34,197,94,.08);  }
  .bg-yellow { background: rgba(234,179,8,.08); }
  .bg-red    { background: rgba(239,68,68,.08);  }

  .dim-row {
    display: grid;
    grid-template-columns: 140px 1fr 48px;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
  }
  .dim-row:last-child { border-bottom: none; }
  .dim-name   { font-size: 13px; }
  .dim-weight { font-size: 11px; color: var(--muted); }
  .bar-track  { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
  .bar-fill   {
    height: 100%; border-radius: 3px;
    transition: width .6s cubic-bezier(.25,.8,.25,1);
    width: 0;
  }
  .dim-score  { font-size: 13px; font-weight: 600; text-align: right; }

  .tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
  .tag  {
    font-size: 11px; padding: 3px 10px;
    border-radius: 20px; border: 1px solid; font-weight: 500;
  }
  .tag-required { color: var(--red);    border-color: rgba(239,68,68,.4);  background: rgba(239,68,68,.06); }
  .tag-preferred{ color: var(--yellow); border-color: rgba(234,179,8,.4);  background: rgba(234,179,8,.06); }

  .suggestion {
    padding: 12px;
    border-radius: 8px;
    border-left: 3px solid;
    background: var(--bg);
    margin-bottom: 8px;
    font-size: 13px;
    line-height: 1.5;
  }
  .suggestion .dim-tag {
    font-size: 10px; font-weight: 600;
    letter-spacing: .5px; text-transform: uppercase;
    opacity: .6; display: block; margin-bottom: 3px;
  }
  .s-high   { border-color: var(--red);    }
  .s-medium { border-color: var(--yellow); }
  .s-low    { border-color: var(--green);  }

  .section-title {
    font-size: 11px; font-weight: 600;
    letter-spacing: .6px; text-transform: uppercase;
    color: var(--muted); margin-bottom: 14px;
  }

  .error-banner {
    background: rgba(239,68,68,.1);
    border: 1px solid rgba(239,68,68,.3);
    color: var(--red);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    margin-top: 12px;
    display: none;
  }

  .summary-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px; }
  .pill {
    font-size: 11px;
    background: var(--border);
    color: var(--muted);
    padding: 3px 10px;
    border-radius: 20px;
  }

  #results { display: none; }

  .mode-row { margin-top: 16px; }
  .mode-toggle { display: flex; gap: 10px; margin-top: 6px; }
  .mode-opt {
    display: flex; align-items: center; gap: 8px;
    cursor: pointer; padding: 10px 14px;
    border: 1.5px solid var(--border); border-radius: 8px;
    transition: border-color .15s, background .15s;
    flex: 1;
  }
  .mode-opt:has(input:checked) { border-color: var(--accent); background: rgba(99,102,241,.05); }
  .mode-opt input[type=radio] { display: none; }
  .mode-badge {
    font-size: 11px; font-weight: 700; padding: 2px 8px;
    border-radius: 4px; letter-spacing: .3px;
  }
  .mode-badge.local { background: rgba(34,197,94,.15); color: var(--green); }
  .mode-badge.llm   { background: rgba(99,102,241,.15); color: var(--accent); }
  .mode-desc { font-size: 11px; color: var(--muted); }
</style>
</head>
<body>
<div class="container">

  <header>
    <h1>ATS CV Evaluator</h1>
    <p>Score your resume against a job description using industry-standard ATS criteria.</p>
  </header>

  <div class="card">
    <div class="form-grid">

      <div>
        <label>Your CV</label>
        <div class="drop-zone" id="cv-zone">
          <input type="file" id="cv-file" accept=".pdf,.docx">
          <div class="icon">&#128196;</div>
          <div class="hint">Drop PDF or DOCX here</div>
          <div class="filename" id="cv-name"></div>
        </div>
      </div>

      <div>
        <label>Job Description</label>
        <textarea id="jd-text" placeholder="Paste the job description here&#8230;"></textarea>
      </div>

    </div>

    <div class="mode-row">
      <label class="mode-label">Extraction Mode</label>
      <div class="mode-toggle">
        <label class="mode-opt">
          <input type="radio" name="mode" value="local" checked>
          <span class="mode-badge local">Local</span>
          <span class="mode-desc">Fast · Private · No API key needed</span>
        </label>
        <label class="mode-opt">
          <input type="radio" name="mode" value="llm">
          <span class="mode-badge llm">LLM</span>
          <span class="mode-desc">More accurate · Requires Claude API key</span>
        </label>
      </div>
      <div id="api-key-row" style="display:none; margin-top:10px;">
        <input type="password" id="api-key-input" placeholder="sk-ant-..."
               style="width:100%; background:var(--bg); border:1.5px solid var(--border); border-radius:8px; color:var(--text); font-size:13px; padding:10px 12px; outline:none; font-family:inherit;">
      </div>
    </div>

    <button class="btn" id="eval-btn" onclick="runEval()">
      <span class="spinner" id="spinner"></span>
      <span id="btn-label">Evaluate</span>
    </button>

    <div class="error-banner" id="error-box"></div>
  </div>

  <div id="results">

    <div class="card" id="hero-card" style="padding:0">
      <div class="score-hero">
        <div class="score-circle" id="score-circle">
          <span class="num" id="score-num">0</span>
          <span class="denom">/100</span>
        </div>
        <div class="score-meta">
          <h2 id="score-label"></h2>
          <p id="cv-summary-txt"></p>
          <p id="jd-summary-txt" style="margin-top:2px"></p>
          <p id="report-mode" style="margin-top:4px; font-size:11px; opacity:.5"></p>
          <div class="summary-row" id="score-pills"></div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">Score Breakdown</div>
      <div id="dims"></div>
    </div>

    <div class="card" id="kw-card" style="display:none">
      <div class="section-title">Missing Keywords</div>
      <div class="tags" id="kw-tags"></div>
    </div>

    <div class="card" id="sug-card" style="display:none">
      <div class="section-title">Actionable Suggestions</div>
      <div id="suggestions"></div>
    </div>

  </div>
</div>

<script>
const cvZone = document.getElementById('cv-zone');
const cvFile = document.getElementById('cv-file');
const cvName = document.getElementById('cv-name');

cvFile.addEventListener('change', () => { cvName.textContent = cvFile.files[0] ? cvFile.files[0].name : ''; });
cvZone.addEventListener('dragover', e => { e.preventDefault(); cvZone.classList.add('dragover'); });
cvZone.addEventListener('dragleave', () => cvZone.classList.remove('dragover'));
cvZone.addEventListener('drop', e => {
  e.preventDefault();
  cvZone.classList.remove('dragover');
  var f = e.dataTransfer.files[0];
  if (f) { var dt = new DataTransfer(); dt.items.add(f); cvFile.files = dt.files; cvName.textContent = f.name; }
});

function scoreClass(s) { return s >= 80 ? 'green' : s >= 60 ? 'yellow' : 'red'; }
function scoreLabel(s) { return s >= 80 ? 'Strong Match' : s >= 60 ? 'Acceptable' : s >= 40 ? 'At Risk' : 'Low Match'; }
function barColor(s)   { return s >= 80 ? 'var(--green)' : s >= 60 ? 'var(--yellow)' : 'var(--red)'; }
function fmtDim(name)  { return name.replace(/_/g, ' ').replace(/\\b\\w/g, function(c) { return c.toUpperCase(); }); }

async function runEval() {
  var file = cvFile.files[0];
  var jd   = document.getElementById('jd-text').value.trim();
  if (!file) { showError('Please upload your CV.'); return; }
  if (!jd)   { showError('Please enter the job description.'); return; }
  hideError();

  var btn = document.getElementById('eval-btn');
  var sp  = document.getElementById('spinner');
  var lbl = document.getElementById('btn-label');
  btn.disabled = true;
  sp.style.display = 'block';
  lbl.textContent = 'Analyzing…';

  var mode = document.querySelector('input[name="mode"]:checked').value;

  if (mode === 'llm') {
    var apiKey = document.getElementById('api-key-input').value.trim();
    if (!apiKey) {
      showError('LLM mode requires a Claude API key (sk-ant-...).');
      btn.disabled = false; sp.style.display = 'none'; lbl.textContent = 'Evaluate';
      return;
    }
  }

  var form = new FormData();
  form.append('cv_file', file);
  form.append('jd_text', jd);
  form.append('mode', mode);

  if (mode === 'llm') {
    var apiKey = document.getElementById('api-key-input').value.trim();
    form.append('api_key', apiKey);
  }

  try {
    var res  = await fetch('/evaluate', { method: 'POST', body: form });
    var data = await res.json();
    if (!res.ok) { showError(data.detail || 'An error occurred.'); return; }
    renderReport(data);
  } catch(err) {
    showError('Network error — is the server running?');
  } finally {
    btn.disabled = false;
    sp.style.display = 'none';
    lbl.textContent = 'Evaluate';
  }
}

function renderReport(d) {
  var cls = scoreClass(d.total_score);
  var lbl = scoreLabel(d.total_score);

  var circle = document.getElementById('score-circle');
  circle.className = 'score-circle ' + cls;
  document.getElementById('hero-card').className = 'card bg-' + cls;
  document.getElementById('score-num').textContent = Math.round(d.total_score);
  document.getElementById('score-label').textContent = lbl;
  document.getElementById('cv-summary-txt').textContent = d.cv_summary;
  document.getElementById('jd-summary-txt').textContent = d.jd_summary;

  var modeEl = document.getElementById('report-mode');
  if (modeEl) modeEl.textContent = 'Mode: ' + (d.extraction_mode || 'local');

  var pills = document.getElementById('score-pills');
  pills.innerHTML = '';
  var top3 = d.dimensions.slice().sort(function(a,b){ return b.raw_score - a.raw_score; }).slice(0,3);
  top3.forEach(function(dim) {
    var p = document.createElement('span');
    p.className = 'pill';
    p.textContent = fmtDim(dim.name) + ' ' + Math.round(dim.raw_score) + '%';
    pills.appendChild(p);
  });

  var dimsEl = document.getElementById('dims');
  dimsEl.innerHTML = '';
  var sorted = d.dimensions.slice().sort(function(a,b){ return a.raw_score - b.raw_score; });
  sorted.forEach(function(dim) {
    var row = document.createElement('div');
    row.className = 'dim-row';

    var nameDiv = document.createElement('div');
    var n = document.createElement('div'); n.className = 'dim-name'; n.textContent = fmtDim(dim.name);
    var w = document.createElement('div'); w.className = 'dim-weight'; w.textContent = Math.round(dim.weight * 100) + '% weight';
    nameDiv.appendChild(n); nameDiv.appendChild(w);

    var track = document.createElement('div'); track.className = 'bar-track';
    var fill  = document.createElement('div'); fill.className = 'bar-fill';
    fill.style.background = barColor(dim.raw_score);
    fill.dataset.score = dim.raw_score;
    track.appendChild(fill);

    var scoreDiv = document.createElement('div');
    scoreDiv.className = 'dim-score ' + scoreClass(dim.raw_score);
    scoreDiv.textContent = Math.round(dim.raw_score);

    row.appendChild(nameDiv);
    row.appendChild(track);
    row.appendChild(scoreDiv);
    dimsEl.appendChild(row);
  });

  requestAnimationFrame(function() {
    document.querySelectorAll('.bar-fill').forEach(function(bar) {
      bar.style.width = bar.dataset.score + '%';
    });
  });

  var kwCard = document.getElementById('kw-card');
  var kwTags = document.getElementById('kw-tags');
  kwTags.innerHTML = '';
  if (d.missing_keywords && d.missing_keywords.length) {
    kwCard.style.display = 'block';
    d.missing_keywords.forEach(function(kw) {
      var t = document.createElement('span');
      t.className = 'tag tag-' + kw.severity;
      t.textContent = kw.keyword;
      kwTags.appendChild(t);
    });
  } else {
    kwCard.style.display = 'none';
  }

  var sugCard = document.getElementById('sug-card');
  var sugEl   = document.getElementById('suggestions');
  sugEl.innerHTML = '';
  var shown = d.suggestions.filter(function(s){ return s.priority !== 'low'; }).slice(0, 6);
  if (shown.length) {
    sugCard.style.display = 'block';
    shown.forEach(function(s) {
      var el = document.createElement('div');
      el.className = 's-' + s.priority + ' suggestion';
      var tag = document.createElement('span'); tag.className = 'dim-tag'; tag.textContent = fmtDim(s.dimension);
      el.appendChild(tag);
      el.appendChild(document.createTextNode(s.message));
      sugEl.appendChild(el);
    });
  } else {
    sugCard.style.display = 'none';
  }

  document.getElementById('results').style.display = 'block';
  document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(msg) { var b = document.getElementById('error-box'); b.textContent = msg; b.style.display = 'block'; }
function hideError()    { document.getElementById('error-box').style.display = 'none'; }

document.getElementById('jd-text').addEventListener('keydown', function(e) {
  if (e.ctrlKey && e.key === 'Enter') runEval();
});

document.querySelectorAll('input[name="mode"]').forEach(function(radio) {
  radio.addEventListener('change', function() {
    var apiRow = document.getElementById('api-key-row');
    apiRow.style.display = this.value === 'llm' ? 'block' : 'none';
  });
});
</script>
</body>
</html>"""
