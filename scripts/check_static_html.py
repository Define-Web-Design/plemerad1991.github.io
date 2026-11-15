#!/usr/bin/env python3
"""Offline integrity checks for tracked/static HTML sources, not HTML conformance."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def check(root: Path) -> dict[str, object]:
    root = root.resolve()
    paths = sorted((p for p in root.rglob("*")
                    if p.is_file() and p.suffix.lower() in {".html", ".htm"}
                    and ".git" not in p.relative_to(root).parts),
                   key=lambda p: p.relative_to(root).as_posix())
    failures: list[str] = []
    if not (root / "index.html").is_file():
        failures.append("index.html is missing")
    if not paths:
        failures.append("No HTML pages found")
    digest = hashlib.sha256()
    for path in paths:
        rel = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        if not raw.strip():
            failures.append(f"{rel!r}: empty page")
        elif b"\x00" in raw:
            failures.append(f"{rel!r}: NUL byte in page")
        else:
            try:
                raw.decode("utf-8")
            except UnicodeDecodeError:
                failures.append(f"{rel!r}: invalid UTF-8")
        digest.update(rel.encode("utf-8") + b"\x00" + hashlib.sha256(raw).digest())
    return {"html_files": len(paths), "sha256_manifest": digest.hexdigest(),
            "failures": failures, "scope": "UTF-8 / non-empty / NUL / index only"}


def main() -> int:
    report = check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd())
    print(json.dumps(report, sort_keys=True))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
