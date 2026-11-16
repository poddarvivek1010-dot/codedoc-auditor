import streamlit as st
import re
from scanner import SECRET_PATTERNS

st.set_page_config(page_title="CodeDoc Auditor", page_icon="🛡️", layout="centered")

# Minimalist custom styling
st.markdown("""
    <style>
    .block-container { padding-top: 2.5rem; padding-bottom: 2.5rem; max-width: 760px; }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 18px;
    }
    .check-row {
        background-color: #161B22;
        border: 1px solid #21262D;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("CodeDoc Auditor")
st.caption("Pre-commit security & code-hygiene verification for clean GitHub releases.")

code_input = st.text_area(
    "Source Code",
    height=230,
    placeholder='print("Hello, World!")',
    label_visibility="collapsed"
)

col1, col2 = st.columns([2, 1])
with col1:
    has_readme = st.checkbox("Repository includes a README.md file", value=True, help="Uncheck if auditing a full repository that lacks documentation.")
with col2:
    run_btn = st.button("Run Audit", use_container_width=True, type="primary")

if run_btn:
    if not code_input.strip():
        st.info("Paste source code above to begin inspection.")
    else:
        lines = code_input.splitlines()
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
                    secrets_found.append(f"Line {line_num} — {label}")

            if todo_tag in line or fixme_tag in line:
                todos_found.append(f"Line {line_num} — `{stripped}`")

            if re.search(r"(localhost|127\.0\.0\.1|debug\s*=\s*True)", line, re.IGNORECASE):
                debug_found.append(f"Line {line_num} — `{stripped}`")

        # Category scoring (100 pts total)
        sec_pts = max(0, 50 - (len(secrets_found) * 50))
        env_pts = max(0, 15 - (len(debug_found) * 5))
        hyg_pts = max(0, 15 - (len(todos_found) * 5))
        com_pts = 10 if has_comments else 0
        doc_pts = 10 if has_readme else 0

        total_score = sec_pts + env_pts + hyg_pts + com_pts + doc_pts

        # Status verdict
        if secrets_found:
            verdict = "Blocked — Exposed credentials detected"
            accent = "#F85149"
        elif total_score >= 85:
            verdict = "Ready — Safe to push to repository"
            accent = "#3FB950"
        else:
            verdict = "Review Suggested — Minor hygiene items flagged"
            accent = "#D29922"

        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em;">Audit Readiness Score</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #E6EDF3; margin: 4px 0;">{total_score} <span style="font-size: 1.1rem; color: #8B949E;">/ 100</span></div>
            <div style="font-size: 0.95rem; color: {accent}; font-weight: 500;">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Inspection Breakdown")

        checks = [
            (not secrets_found, "Credential & API Key Isolation", f"{sec_pts}/50 pts", "No hardcoded keys or passwords found" if not secrets_found else f"{len(secrets_found)} secret(s) exposed — move to .env"),
            (not debug_found, "Environment & Debug Safety", f"{env_pts}/15 pts", "No localhost URLs or debug flags" if not debug_found else f"{len(debug_found)} local/debug reference(s) found"),
            (not todos_found, "Code Hygiene & Tag Resolution", f"{hyg_pts}/15 pts", "Zero unresolved code tags" if not todos_found else f"{len(todos_found)} leftover note(s) found"),
            (has_comments, "Inline Code Readability", f"{com_pts}/10 pts", "Includes explanatory comments/docstrings" if has_comments else "Add brief comments for maintainability"),
            (has_readme, "Repository Documentation", f"{doc_pts}/10 pts", "README.md confirmed" if has_readme else "Include a README.md before publishing"),
        ]

        for passed, title, pts, detail in checks:
            icon = "✓" if passed else "✕"
            icon_color = "#3FB950" if passed else "#8B949E"
            st.markdown(f"""
            <div class="check-row">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span><strong style="color: {icon_color}; margin-right: 8px;">{icon}</strong> <strong>{title}</strong></span>
                    <span style="color: #8B949E; font-size: 0.85rem;">{pts}</span>
                </div>
                <div style="color: #8B949E; font-size: 0.84rem; margin-left: 20px; margin-top: 2px;">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

        if secrets_found or debug_found or todos_found:
            with st.expander("View Flagged Line Numbers", expanded=True):
                for s in secrets_found:
                    st.write(f"• **Credential:** {s}")
                for d in debug_found:
                    st.write(f"• **Environment:** {d}")
                for t in todos_found:
                    st.write(f"• **Code Note:** {t}")
