"""Fail on common committed credential shapes without printing secret values."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {
    "",
    ".env",
    ".example",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
ASSIGNMENT = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSCODE|CREDENTIAL)[A-Za-z0-9_]*)\s*=\s*([^#\s]+)",
    re.IGNORECASE,
)
HIGH_RISK = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"),
    re.compile(
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
    ),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)
SAFE_VALUES = {
    "",
    "replace_me",
    "placeholder",
    "example",
    "your_key_here",
    "changeme",
}
SAFE_PREFIXES = (
    "os.getenv(",
    "environ.get(",
    "process.env.",
    "system.getenv(",
    "getenv(",
)


def scan() -> list[tuple[Path, int, str]]:
    findings: list[tuple[Path, int, str]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            assignment = ASSIGNMENT.search(line)
            assigned_value = assignment.group(2).strip().lower() if assignment else ""
            if (
                assignment
                and assigned_value not in SAFE_VALUES
                and not assigned_value.startswith(SAFE_PREFIXES)
            ):
                findings.append(
                    (path.relative_to(ROOT), line_number, assignment.group(1))
                )
            elif any(pattern.search(line) for pattern in HIGH_RISK):
                findings.append(
                    (
                        path.relative_to(ROOT),
                        line_number,
                        "high-risk credential pattern",
                    )
                )
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("Potential committed credentials detected. Values are redacted:")
        for path, line_number, label in findings:
            print(f"- {path}:{line_number} ({label})")
        return 1
    print("No common committed credential patterns detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
