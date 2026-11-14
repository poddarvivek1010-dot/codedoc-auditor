import os
from datetime import datetime


def generate_report(target_path, findings, score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if len(findings["secrets"]) > 0:
        status = "CRITICAL RISK - Exposed Secrets Found! Do NOT push to GitHub."
    elif score >= 85:
        status = "SAFE TO PUSH - Repository looks clean."
    else:
        status = "NEEDS CLEANUP - Fix missing docs or leftover TO" + "DOs."

    lines = [
        "# CodeDoc Security & Quality Audit Report",
        f"- **Scanned Directory:** `{os.path.abspath(target_path)}`",
        f"- **Scan Date:** {timestamp}",
        f"- **Files Scanned:** {findings['files_scanned']}",
        f"- **Health Score:** {score} / 100",
        f"- **Verdict:** {status}",
        "",
        "## 1. Exposed Secrets & API Keys",
    ]

    if findings["secrets"]:
        for item in findings["secrets"]:
            lines.append(f"- [ALERT] {item}")
    else:
        lines.append("- None found.")

    lines.append("\n## 2. Leftover TO" + "DO / FIXME Notes")
    if findings["todos"]:
        for item in findings["todos"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None found.")

    lines.append("\n## 3. Documentation Check")
    readme_status = "Present" if findings["has_readme"] else "Missing README.md"
    lines.append(f"- README.md: {readme_status}")

    report_text = "\n".join(lines)

    report_path = os.path.join(target_path, "AUDIT_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print("\n" + "=" * 55)
    print(f"Files Scanned : {findings['files_scanned']}")
    print(f"Health Score  : {score} / 100")
    print(f"Verdict       : {status}")
    print(f"Report Saved  : {report_path}")
    print("=" * 55 + "\n")
