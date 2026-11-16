import streamlit as st
import re
from scanner import SECRET_PATTERNS

st.set_page_config(page_title="CodeDoc Auditor", page_icon="🛡️")

st.title("🛡️ CodeDoc Security & Hygiene Auditor")
st.write("Paste your Python, JavaScript, or `.env` code below to check for exposed API keys, passwords, and unresolved tags before pushing to GitHub.")

code_input = st.text_area("Paste Code Here:", height=220, placeholder='print("Hello, World!")')

if st.button("Run Security Audit"):
    if not code_input.strip():
        st.warning("Please paste some code first.")
    else:
        secrets_found = []
        todos_found = []
        todo_tag = "TO" + "DO"
        fixme_tag = "FIX" + "ME"

        for line_num, line in enumerate(code_input.splitlines(), start=1):
            for label, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, line):
                    secrets_found.append(f"Line {line_num}: Potential **{label}** detected")
            if todo_tag in line or fixme_tag in line:
                todos_found.append(f"Line {line_num}: `{line.strip()}`")

        # Calculate points per category (Total = 100 pts)
        secrets_pts = max(0, 80 - (len(secrets_found) * 40))
        hygiene_pts = max(0, 20 - (len(todos_found) * 5))
        score = secrets_pts + hygiene_pts

        st.subheader(f"Code Security Score: {score} / 100")

        if secrets_found:
            st.error("CRITICAL RISK: Exposed Secrets Found! Do NOT push to GitHub.")
        elif score == 100:
            st.success("PERFECT SCORE (100/100): Clean code with zero exposed secrets or leftover tags — safe to push!")
        else:
            st.warning("NEEDS CLEANUP: Fix the minor notes listed below before pushing.")

        # --- Visual Audit Checklist ---
        st.markdown("### 📋 Audit Checklist & Points Breakdown")

        if not secrets_found:
            st.write(f"✅ **No Exposed API Keys or Passwords** (+{secrets_pts}/80 pts)")
        else:
            st.write(f"❌ **Exposed Secrets Detected ({len(secrets_found)} found)** (+{secrets_pts}/80 pts) — *Move keys to a `.env` file.*")

        if not todos_found:
            st.write(f"✅ **No Unresolved TODO / FIXME Tags** (+{hygiene_pts}/20 pts)")
        else:
            st.write(f"⚠️ **Leftover Code Notes ({len(todos_found)} found)** (+{hygiene_pts}/20 pts) — *Resolve or remove before release.*")

        # --- Detailed Line Warnings (if any) ---
        if secrets_found:
            st.markdown("### 🚨 Secret Leak Details")
            for item in secrets_found:
                st.write(f"- {item}")

        if todos_found:
            st.markdown("### ⚠️ Leftover Note Details")
            for item in todos_found:
                st.write(f"- {item}")
