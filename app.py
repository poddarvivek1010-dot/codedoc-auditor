import streamlit as st
import re
from scanner import SECRET_PATTERNS

st.set_page_config(page_title="CodeDoc Auditor", page_icon="🛡️")

st.title("🛡️ CodeDoc Security & Hygiene Auditor")
st.write("Paste your Python, JavaScript, or `.env` code below to check for exposed API keys, passwords, and leftover tags before pushing to GitHub.")

code_input = st.text_area("Paste Code Here:", height=220, placeholder='api_key = "AIzaSy..."')
has_readme = st.checkbox("My repository includes a README.md file", value=True)

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

        score = 100 - (len(secrets_found) * 40) - (len(todos_found) * 5) - (0 if has_readme else 15)
        score = max(0, score)

        st.subheader(f"Repository Health Score: {score} / 100")

        if secrets_found:
            st.error("CRITICAL RISK: Exposed Secrets Found! Do NOT push to GitHub.")
            for item in secrets_found:
                st.write(f"- 🚨 {item}")
        elif score >= 85:
            st.success("SAFE TO PUSH: Your code looks clean.")
        else:
            st.warning("NEEDS CLEANUP: Fix missing documentation or leftover notes.")

        if todos_found:
            st.write("**Leftover Code Notes:**")
            for item in todos_found:
                st.write(f"- ⚠️ {item}")
