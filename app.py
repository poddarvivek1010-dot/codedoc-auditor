import ast
import re
import streamlit as st
from scanner import SECRET_PATTERNS

st.set_page_config(page_title="CodeDoc Auditor", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1180px; }
    .panel-card { background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 20px 24px; margin-bottom: 16px; }
    .stat-box { background-color: #0D1117; border: 1px solid #21262D; border-radius: 8px; padding: 12px 16px; }
    .check-row { background-color: #0D1117; border: 1px solid #21262D; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; background-color: #21262D; color: #8B949E; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- Top Navigation Header ---
head_left, head_right = st.columns([2.5, 1])
with head_left:
  st.markdown("## CodeDoc Auditor")
  st.caption(
      "Static security, syntax & pre-commit hygiene console for GitHub"
      " repositories."
  )
with head_right:
  st.markdown(
      '<div style="text-align:right; padding-top:14px;">'
      '<span class="badge">v1.3 • AST + Regex Engine</span> '
      '<span class="badge">Zero-Dependency</span>'
      "</div>",
      unsafe_allow_html=True,
  )

st.divider()

# --- Sample Code Preset ---
SAMPLE_CODE = """# User authentication helper
import os

API_ENDPOINT = "http://127.0.0"
api_key = "AIzaSyD9823ExampleExposedKey1234567890"

def connect_service():
    # TODO: Add retry logic before production release
    return True
"""

if "code_buffer" not in st.session_state:
  st.session_state.code_buffer = ""

# --- Main Two-Column Dashboard ---
left_col, right_col = st.columns([1.15, 1], gap="large")

with left_col:
  st.markdown("#### 1. Source Code Input")
  t1, t2 = st.columns(2)
  with t1:
    if st.button("Load Sample Snippet", use_container_width=True):
      st.session_state.code_buffer = SAMPLE_CODE
  with t2:
    if st.button("Clear Editor", use_container_width=True):
      st.session_state.code_buffer = ""

  code_input = st.text_area(
      "Editor",
      value=st.session_state.code_buffer,
      height=310,
      placeholder='print("Hello, World!")',
      label_visibility="collapsed",
  )
  st.session_state.code_buffer = code_input

  st.markdown("#### 2. Optional Repository Extras")
  o1, o2 = st.columns(2)
  with o1:
    has_readme = st.checkbox("Includes README.md (Optional)", value=True)
  with o2:
    has_gitignore = st.checkbox("Includes .gitignore (Optional)", value=True)

  st.button(
      "Run Pre-Commit Security Audit", type="primary", use_container_width=True
  )

with right_col:
  st.markdown("#### 3. Live Audit Report")
  active_code = code_input.strip()
  lines = code_input.splitlines() if active_code else []
  secrets_found, todos_found, debug_found = [], [], []
  has_comments = False
  syntax_error_msg = None
  todo_tag, fixme_tag = "TO" + "DO", "FIX" + "ME"

  if active_code:
    # 1. Python AST Syntax & Indentation Check
    try:
      ast.parse(code_input)
    except SyntaxError as e:
      syntax_error_msg = f"Line {e.lineno} • {e.msg}"

    # 2. Line-by-Line Security & Hygiene Checks
    for line_num, line in enumerate(lines, start=1):
      stripped = line.strip()
      if stripped.startswith(("#", "//", "/*", '"""', "'''")):
        has_comments = True
      for label, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, line):
          secrets_found.append(f"Line {line_num} • {label}")
      if todo_tag in line or fixme_tag in line:
        todos_found.append(f"Line {line_num} • `{stripped}`")
      if re.search(
          r"(localhost|127\.0\.0\.1|debug\s*=\s*True)", line, re.IGNORECASE
      ):
        debug_found.append(f"Line {line_num} • `{stripped}`")

  if not active_code:
    st.markdown(
        '<div class="panel-card"><div'
        ' style="font-size:0.82rem;color:#8B949E;text-transform:uppercase;">Engine'
        ' Status</div><div'
        ' style="font-size:1.6rem;font-weight:700;color:#E6EDF3;margin:6px'
        ' 0;">Awaiting Source Input</div><div'
        ' style="font-size:0.92rem;color:#8B949E;">Paste your Python script on'
        " the left or click <strong>Load Sample Snippet</strong> to verify"
        " syntax compilation, credential safety, and repository"
        " hygiene.</div></div>",
        unsafe_allow_html=True,
    )
    for rule_title, weight, desc in [
        (
            "Credential & Secret Isolation",
            "40 pts",
            (
                "Scans for Google/Firebase keys, AWS tokens, and hardcoded"
                " passwords"
            ),
        ),
        (
            "Python Syntax Validation (AST)",
            "20 pts",
            (
                "Verifies code compiles cleanly with zero syntax or indentation"
                " errors"
            ),
        ),
        (
            "Environment & Debug Hygiene",
            "10 pts",
            "Detects localhost URLs, 127.0.0.1 endpoints, and debug=True flags",
        ),
        (
            "Unresolved Tag & Readability Check",
            "15 pts",
            (
                "Checks for leftover TODO/FIXME notes (10 pts) and inline"
                " comments (5 pts)"
            ),
        ),
        (
            "Optional Repository Extras",
            "15 pts",
            "Bonus points for README.md (10 pts) and .gitignore (5 pts)",
        ),
    ]:
      st.markdown(
          f'<div class="check-row"><div style="display:flex;justify-content:space-between;"><strong style="color:#E6EDF3;">{rule_title}</strong><span style="color:#58A6FF;font-size:0.85rem;font-weight:600;">{weight}</span></div><div style="color:#8B949E;font-size:0.83rem;margin-top:3px;">{desc}</div></div>',
          unsafe_allow_html=True,
      )
  else:
    sec_pts = max(0, 40 - (len(secrets_found) * 40))
    syn_pts = 0 if syntax_error_msg else 20
    env_pts = max(0, 10 - (len(debug_found) * 5))
    hyg_pts = max(0, 10 - (len(todos_found) * 5)) + (5 if has_comments else 0)
    doc_pts = (10 if has_readme else 0) + (5 if has_gitignore else 0)
    total_score = sec_pts + syn_pts + env_pts + hyg_pts + doc_pts

    if secrets_found:
      verdict, accent = "Blocked — Exposed Credentials Detected", "#F85149"
    elif syntax_error_msg:
      verdict, accent = "Blocked — Python Syntax Error Found", "#F85149"
    elif total_score >= 85:
      verdict, accent = "Verified — Safe to Push to GitHub", "#3FB950"
    else:
      verdict, accent = (
          "Safe to Push — Optional Improvements Available",
          "#58A6FF",
      )

    m1, m2, m3 = st.columns(3)
    m1.markdown(
        f'<div class="stat-box"><div style="color:#8B949E;font-size:0.78rem;">READINESS SCORE</div><div style="font-size:1.5rem;font-weight:700;color:{accent};">{total_score}/100</div></div>',
        unsafe_allow_html=True,
    )
    m2.markdown(
        f'<div class="stat-box"><div style="color:#8B949E;font-size:0.78rem;">LINES SCANNED</div><div style="font-size:1.5rem;font-weight:700;color:#E6EDF3;">{len(lines)}</div></div>',
        unsafe_allow_html=True,
    )
    issues_total = (
        len(secrets_found)
        + (1 if syntax_error_msg else 0)
        + len(debug_found)
        + len(todos_found)
    )
    m3.markdown(
        f'<div class="stat-box"><div style="color:#8B949E;font-size:0.78rem;">ISSUES DETECTED</div><div style="font-size:1.5rem;font-weight:700;color:#E6EDF3;">{issues_total}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="margin:12px 0;font-weight:600;color:{accent};">Status: {verdict}</div>',
        unsafe_allow_html=True,
    )

    for passed, title, pts, detail in [
        (
            not secrets_found,
            "Credential & Secret Isolation",
            f"{sec_pts}/40 pts",
            "Zero hardcoded keys or passwords"
            if not secrets_found
            else f"{len(secrets_found)} secret(s) detected — move to .env",
        ),
        (
            not syntax_error_msg,
            "Python Syntax Validation (AST)",
            f"{syn_pts}/20 pts",
            "Valid Python syntax — compiles cleanly"
            if not syntax_error_msg
            else f"SyntaxError: {syntax_error_msg}",
        ),
        (
            not debug_found,
            "Environment & Debug Hygiene",
            f"{env_pts}/10 pts",
            "No localhost or debug=True flags"
            if not debug_found
            else f"{len(debug_found)} local/debug endpoint(s) flagged",
        ),
        (
            not todos_found and has_comments,
            "Code Hygiene & Readability",
            f"{hyg_pts}/15 pts",
            "Clean tags & inline comments present"
            if (not todos_found and has_comments)
            else "Check for leftover TODOs or add brief comments",
        ),
        (
            has_readme and has_gitignore,
            "Optional Repository Extras",
            f"{doc_pts}/15 pts",
            "README.md & .gitignore included"
            if (has_readme and has_gitignore)
            else (
                "Optional: Adding README.md or .gitignore earns bonus points"
            ),
        ),
    ]:
      icon = (
          "✓"
          if passed
          else "✕"
          if ("Credential" in title or "Syntax" in title)
          else "•"
      )
      icon_color = (
          "#3FB950" if passed else "#F85149" if icon == "✕" else "#8B949E"
      )
      st.markdown(
