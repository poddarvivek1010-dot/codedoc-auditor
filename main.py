import os
import sys
from scanner import scan_directory
from scorer import calculate_health_score
from reporter import generate_report


def main():
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.exists(target_path):
        print(f"Error: Folder '{target_path}' does not exist.")
        return

    print(f"Scanning '{target_path}'...")
    findings = scan_directory(target_path)
    score = calculate_health_score(findings)
    generate_report(target_path, findings, score)


if __name__ == "__main__":
    main()
