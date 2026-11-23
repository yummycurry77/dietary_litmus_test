"""Scan a submission tree for common accidental identity leaks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TEXT_EXTENSIONS = {".md", ".txt", ".py", ".csv", ".json", ".yml", ".yaml", ".srt", ".vtt"}
PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "windows_absolute_path": re.compile(r"\b[A-Z]:\\Users\\", re.I),
    "api_key_marker": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{10,}|AIza[A-Za-z0-9_-]{20,})\b"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan text files for common identity leaks")
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()

    findings: list[str] = []
    for path in args.root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"{path}:{line_number}: {label}")

    if findings:
        print("[anonymity check] FINDINGS")
        print("\n".join(findings))
        return 1
    print("[anonymity check] PASS: no common email, absolute-path, or API-key patterns found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
