import os
import re

SECRET_PATTERNS = {
    "Generic API Key": r"(?i)(api_key|apikey|secret_key)\s*=\s*['\"][A-Za-z0-9_\-]{12,}['\"]",
    "Google / Firebase API Key": r"AIza[0-9A-Za-z\-_]{35}",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Hardcoded Password": r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{4,}['\"]",
}


def scan_directory(target_path):
    findings = {
        "secrets": [],
        "todos": [],
        "files_scanned": 0,
        "has_readme": False,
    }

    todo_tag = "TO" + "DO"
    fixme_tag = "FIX" + "ME"

    for root, _, files in os.walk(target_path):
        if ".git" in root or "__pycache__" in root:
            continue

        for file_name in files:
            if file_name == "AUDIT_REPORT.md":
                continue
            if file_name.lower() == "readme.md":
                findings["has_readme"] = True
            if not file_name.endswith((".py", ".js", ".env", ".txt", ".md")):
                continue

            findings["files_scanned"] += 1
            file_path = os.path.join(root, file_name)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        for label, pattern in SECRET_PATTERNS.items():
                            if re.search(pattern, line):
                                findings["secrets"].append(
                                    f"{file_name} (Line {line_num}): Potential {label}"
                                )
                        if todo_tag in line or fixme_tag in line:
                            findings["todos"].append(
                                f"{file_name} (Line {line_num}): {line.strip()}"
                            )
            except OSError:
                continue

    return findings
