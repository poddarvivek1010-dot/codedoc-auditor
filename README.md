# CodeDoc Auditor

A zero-dependency Python CLI tool that audits local repositories for exposed API keys, hardcoded passwords, unresolved code tags, and missing documentation before pushing code to GitHub.

## Features
- **Secret Detection:** Uses regular expressions to catch Google/Firebase keys (`AIza...`), AWS access keys (`AKIA...`), generic API keys, and hardcoded passwords with exact file and line numbers.
- **Code Hygiene Check:** Flags unresolved `TODO` and `FIXME` comments across `.py`, `.js`, `.env`, `.txt`, and `.md` files.
- **Repository Health Score:** Computes a `0–100` readiness score and exports a structured `AUDIT_REPORT.md` summary.

## Project Structure
- `scanner.py` — Recursively walks target directories and runs pattern checks.
- `scorer.py` — Calculates the `0–100` repository health score based on risk severity.
- `reporter.py` — Prints a terminal verdict and generates `AUDIT_REPORT.md`.
- `main.py` — Command-line interface entry point.

## Usage
Clone the repository and run the scanner against any local project directory:

```bash
git clone https://github.com
cd codedoc-auditor
python3 main.py /path/to/your/project
```

To scan the current directory:
```bash
python3 main.py .
```
