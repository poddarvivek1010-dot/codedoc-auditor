import streamlit as st
import re
from scanner import SECRET_PATTERNS

st.set_page_config(page_title="CodeDoc Auditor", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1180px; }
    .panel-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .stat-box {
        background-color: #0D1117;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
    }
    .check-row {
        background-color: #0D1117;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        background-color: #21262D;
        color: #8B949E;
    }
    </style>
""", unsafe_allow_html=True)

# --- Top Navigation Header ---
head_left, head_right = st.columns([3, 1])
with head_left:
    st.markdown("## CodeDoc Auditor")
    st.caption("Static security & pre-commit hygiene console for GitHub repositories.")
with head_right:
    st.markdown(
        '<div style="text-align:right; padding-top:14px;">'
        '<span class="badge">v1.2 • Static Engine</span> '
        '<span class="badge">Zero-Dependency</span>'
        '</div>',
        unsafe_allow_html=True
    )

st.divider()

# --- Sample Code Preset ---
SAMPLE_CODE = '''# User authentication helper
import os

API_ENDPOINT = "http://127.0.0"
api_key = "AIzaSyD9823ExampleExposedKey1234567890"

def connect_service():
    # TODO: Add retry logic before production release
    return True
'''

if "code_buffer" not in st.session_state:
    st.session_state.code_buffer = ""

# --- Main Two-Column Dashboard ---
left_col, right_col = st.columns([1.15, 1], gap="large")

with left_col:
    st.markdown("#### 1. Source Code Input")
    tool_bar_1, tool_bar_2 = st.columns(2)
    with tool_bar_1:
        if st.button("Load Sample Snippet", use_container_width=True):
            st.session_state.code_buffer = SAMPLE_CODE
    with tool_bar_2:
        if st.button("Clear Editor", use_container_width=True):
            st.session_state.code_buffer = ""

    code_input = st.text_area(
        "Editor",
        value=st.session_state.code_buffer,
        height=310,
        placeholder='print("Hello, World!")',
        label_visibility="collapsed"
    )
    st.session_state.code_buffer = code_input

    st.markdown("#### 2. Optional Repository Extras")
    opt_1, opt_2 = st.columns(2)
    with opt_1:
        has_readme = st.checkbox("Includes README.md (Optional)", value=True)
    with opt_2:
        has_gitignore = st.checkbox("Includes .gitignore (Optional)", value=True)

    run_audit = st.button("Run Pre-Commit Security Audit", type="primary", use_container_width=True)

with right_col:
    st.markdown("#### 3. Live Audit Report")

    active_code = code_input.strip()
    lines = code_input.splitlines() if active_code else []
    secrets_found = []
    todos_found = []
    debug_found = []
    has_comments = False

    todo_tag = "TO" + "DO"
    fixme_tag = "FIX" + "ME"

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "/*", '"""', "'''")):
            has_comments = True

        for label, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, line):
                secrets_found.append(f"Line {line_num} • {label}")

        if todo_tag in line or fixme_tag in line:
            todos_found.append(f"Line {line_num} • `{stripped}`")

        if re.search(r"(localhost|127\.0\.0\.1|debug\s*=\s*True)", line, re.IGNORECASE):
            debug_found.append(f"Line {line_num} • `{stripped}`")

    if not active_code:
        st.markdown("""
        <div class="panel-card">
            <div style="font-size: 0.82rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em;">Engine Status</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #E6EDF3; margin: 6px 0;">Awaiting Source Input</div>
            <div style="font-size: 0.92rem; color: #8B949E;">Paste your script on the left or click <strong>Load Sample Snippet</strong> to inspect how CodeDoc flags leaked credentials, debug endpoints, and optional best-practice extras.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Active Inspection Rules (100-Point Scale)**")
        preview_rules = [
            ("Credential & Secret Isolation", "45 pts", "Scans for Google/Firebase keys, AWS tokens, and hardcoded passwords"),
            ("Environment & Debug Hygiene", "15 pts", "Detects localhost URLs, 127.0.0.1 endpoints, and debug=True flags"),
            ("Unresolved Tag Check", "15 pts", "Flags leftover TODO and FIXME developer notes"),
            ("Inline Code Readability", "10 pts", "Checks for explanatory comments or docstrings"),
            ("Optional Repository Extras", "15 pts", "Bonus points for README.md (10 pts) and .gitignore (5 pts) — optional for single scripts"),
        ]
        for rule_title, weight, desc in preview_rules:
            st.markdown(f"""
            <div class="check-row">
                <div style="display:flex; justify-content:space-between;">
                    <strong style="color:#E6EDF3;">{rule_title}</strong>
                    <span style="color:#58A6FF; font-size:0.85rem; font-weight:600;">{weight}</span>
                </div>
                <div style="color:#8B949E; font-size:0.83rem; margin-top:3px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        sec_pts = max(0, 45 - (len(secrets_found) * 45))
        env_pts = max(0, 15 - (len(debug_found) * 5))
        hyg_pts = max(0, 15 - (len(todos_found) * 5))
        com_pts = 10 if has_comments else 0
        doc_pts = (10 if has_readme else 0) + (5 if has_gitignore else 0)
        total_score = sec_pts + env_pts + hyg_pts + com_pts + doc_pts

        if secrets_found:
            verdict = "Blocked — Exposed Credentials Detected"
            accent = "#F85149"
        elif total_score >= 85:
            verdict = "Verified — Safe to Push to GitHub"
            accent = "#3FB950"
        else:
            verdict = "Safe to Push — Optional Improvements Available"
            accent = "#58A6FF"

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="stat-box"><div style="color:#8B949E;font-size:0.78rem;">READINESS SCORE</div><div style="font-size:1.5rem;font-weight:700;color:{accent};">{total_score}/100</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="stat-box"><div style="color:#8B949E;font-size:0.78rem;">LINES SCANNED</div><div style="font-size:1.5rem;font-weight:700;color:#E6EDF3;">{len(lines)}</div></div>', unsafe_allow_html=True)
        with m3:
            issues_total = len(secrets_found) + len(debug_found) + len(todos_found)
            st.markdown(f'<div class="stat-box"><div style="color:#8B949E;font-size:0.78rem;">SECURITY FLAGS</div><div style="font-size:1.5rem;font-weight:700;color:#E6EDF3;">{issues_total}</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div style="margin: 12px 0; font-weight: 600; color: {accent};">Status: {verdict}</div>', unsafe_allow_html=True)

        doc_detail = "README.md & .gitignore included" if (has_readme and has_gitignore) else "Optional: Adding README.md or .gitignore earns bonus points for multi-file repos"

        checks = [
            (not secrets_found, "Credential & Secret Isolation", f"{sec_pts}/45 pts", "Zero hardcoded keys or passwords" if not secrets_found else f"{len(secrets_found)} secret(s) detected — move to .env"),
            (not debug_found, "Environment & Debug Hygiene", f"{env_pts}/15 pts", "No localhost or debug=True flags" if not debug_found else f"{len(debug_found)} local/debug endpoint(s) flagged"),
            (not todos_found, "Unresolved Tag Check", f"{hyg_pts}/15 pts", "No leftover TODO/FIXME notes" if not todos_found else f"{len(todos_found)} unresolved note(s) found"),
            (has_comments, "Inline Code Readability", f"{com_pts}/10 pts", "Explanatory comments/docstrings present" if has_comments else "Optional: Add brief comments so others can follow your logic"),
            (has_readme and has_gitignore, "Optional Repository Extras", f"{doc_pts}/15 pts", doc_detail),
        ]

        for passed, title, pts, detail in checks:
            icon = "✓" if passed else "•"
            icon_color = "#3FB950" if passed else "#F85149" if ("Credential" in title and not passed) else "#8B949E"
            st.markdown(f"""
            <div class="check-row">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span><strong style="color:{icon_color}; margin-right:8px;">{icon}</strong> <strong>{title}</strong></span>
                    <span style="color:#8B949E; font-size:0.84rem;">{pts}</span>
                </div>
                <div style="color:#8B949E; font-size:0.83rem; margin-left:20px; margin-top:2px;">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

        if secrets_found or debug_found or todos_found:
            with st.expander("Line-Level Diagnostic Output", expanded=True):
                for s in secrets_found:
                    st.write(f"• **Secret:** {s}")
                for d in debug_found:
                    st.write(f"• **Environment:** {d}")
                for t in todos_found:
                    st.write(f"• **Tag:** {t}")

st.markdown("""
    <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #21262D; text-align: center; color: #8B949E; font-size: 0.85rem;">
        Built by <strong style="color: #E6EDF3;">Vivek Kumar</strong> &nbsp;•&nbsp;
        <a href="https://github.com" target="_blank" style="color: #58A6FF; text-decoration: none;">View Source on GitHub</a>
    </div>
""", unsafe_allow_html=True)
