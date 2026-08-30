"""Validate local Markdown links and fenced code blocks."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*.md"):
        if any(part in {".git", ".venv", ".ruff_cache"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if text.count("```") % 2:
            findings.append(f"{path.relative_to(ROOT)}: unbalanced fenced code block")
        for raw_target in LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = unquote(target.split("#", maxsplit=1)[0])
            if relative and not (path.parent / relative).resolve().exists():
                findings.append(
                    f"{path.relative_to(ROOT)}: missing local link target {relative}"
                )

    if findings:
        print("Documentation validation failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Markdown links and fenced code blocks are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
