#!/usr/bin/env python3
"""Fast, dependency-free self-check for the animation-logo-skill package.

Validates the skill without needing Pillow/NumPy/SciPy/FFmpeg so it can run in
CI or as a pre-commit sanity gate. It checks:

- SKILL.md frontmatter: required keys, name matches the directory, and description
  length.
- Referenced relative paths in backticks inside SKILL.md exist.
- Eval fixture files referenced by the evaluation cases point at real paths.
- schemas/motion-spec.schema.json parses and has a sane root.
- evals/evals.json and evals/trigger-queries.json parse and have expected shape.
- The bundled manifest validator passes on the valid fixture and fails on the
  invalid fixture (a behavioral smoke test of validate_motion_spec.py).

Exit code 0 on success, 1 when any check fails.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []
NOTES: list[str] = []

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
BACKTICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|json|py|svg|png))`")


def fail(message: str) -> None:
    ERRORS.append(message)


def note(message: str) -> None:
    NOTES.append(message)


def load_skill_md() -> tuple[dict[str, str], str]:
    path = ROOT / "SKILL.md"
    if not path.exists():
        fail("SKILL.md is missing.")
        return {}, ""
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail("SKILL.md must start with a YAML frontmatter block delimited by ---.")
        return {}, text
    front: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, _, value = line.partition(":")
        front[key.strip()] = value.strip().strip('"')
    body = text[match.end():]
    return front, body


def check_frontmatter(front: dict[str, str]) -> None:
    if not front:
        return
    for key in ("name", "description"):
        if not front.get(key):
            fail(f"SKILL.md frontmatter is missing a non-empty '{key}'.")
    name = front.get("name", "")
    if name and name != ROOT.name:
        fail(f"frontmatter name '{name}' must match the directory name '{ROOT.name}'.")
    description = front.get("description", "")
    if description:
        if len(description) > 1024:
            fail(f"description is {len(description)} chars; keep it under 1024.")
        elif len(description) > 700:
            note(f"description is {len(description)} chars and reads long; tighten when convenient.")


def check_backtick_paths(body: str) -> None:
    seen: set[str] = set()
    for match in BACKTICK_PATH_RE.finditer(body):
        rel = match.group(1)
        if "/" not in rel:
            continue
        if rel in seen:
            continue
        seen.add(rel)
        target = ROOT / rel
        if not target.exists():
            fail(f"SKILL.md references '{rel}' but the path does not exist.")
    if seen:
        note(f"checked {len(seen)} referenced file paths in SKILL.md.")


def check_schema() -> None:
    path = ROOT / "schemas" / "motion-spec.schema.json"
    if not path.exists():
        fail("schemas/motion-spec.schema.json is missing.")
        return
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"motion-spec.schema.json is not valid JSON: {exc}")
        return
    if not isinstance(schema, dict):
        fail("motion-spec.schema.json root must be an object.")
        return
    if schema.get("type") != "object":
        fail("motion-spec.schema.json should describe an object manifest.")
    if schema.get("required"):
        note(f"schema declares {len(schema['required'])} required root fields.")


def check_evals() -> None:
    evals_path = ROOT / "evals" / "evals.json"
    queries_path = ROOT / "evals" / "trigger-queries.json"
    for path in (evals_path, queries_path):
        if not path.exists():
            fail(f"evals/{path.name} is missing.")
    if evals_path.exists():
        try:
            data = json.loads(evals_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"evals.json is not valid JSON: {exc}")
            data = {}
        evals = data.get("evals", [])
        if not isinstance(evals, list) or not evals:
            fail("evals.json must contain a non-empty 'evals' array.")
        else:
            total = 0
            for index, item in enumerate(evals):
                if not item.get("id") or not item.get("prompt"):
                    fail(f"evals[{index}] must have 'id' and 'prompt'.")
                assertions = item.get("assertions", [])
                if not assertions:
                    fail(f"evals[{index}] ({item.get('id')}) has no assertions.")
                total += len(assertions)
                for rel in item.get("files", []):
                    if not (ROOT / rel).exists():
                        fail(f"evals[{index}] fixture '{rel}' does not exist.")
            note(f"{len(evals)} eval cases covering {total} assertions.")
    if queries_path.exists():
        try:
            queries = json.loads(queries_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"trigger-queries.json is not valid JSON: {exc}")
            queries = []
        if not isinstance(queries, list) or not queries:
            fail("trigger-queries.json must be a non-empty array.")
        else:
            pos = sum(1 for q in queries if q.get("should_trigger"))
            neg = len(queries) - pos
            if pos == 0 or neg == 0:
                fail("trigger-queries.json must include both positive and negative cases.")
            note(f"{pos} positive and {neg} negative trigger queries.")


def check_manifest_validator() -> None:
    script = ROOT / "scripts" / "validate_motion_spec.py"
    valid = ROOT / "evals" / "files" / "valid-motion-spec.json"
    invalid = ROOT / "evals" / "files" / "invalid-motion-spec.json"
    for path in (script, valid, invalid):
        if not path.exists():
            fail(f"expected file missing for validator smoke test: {path.relative_to(ROOT)}")
    if not (script.exists() and valid.exists() and invalid.exists()):
        return
    good = subprocess.run([sys.executable, str(script), str(valid)], capture_output=True, text=True)
    if good.returncode != 0:
        fail(f"valid-motion-spec.json should PASS but returned {good.returncode}: {good.stdout.strip()}")
    bad = subprocess.run([sys.executable, str(script), str(invalid)], capture_output=True, text=True)
    if bad.returncode == 0:
        fail("invalid-motion-spec.json should FAIL but the validator passed it.")
    else:
        note("manifest validator correctly passes the valid fixture and rejects the invalid one.")


def main() -> int:
    front, body = load_skill_md()
    check_frontmatter(front)
    check_backtick_paths(body)
    check_schema()
    check_evals()
    check_manifest_validator()

    for message in NOTES:
        print(f"note: {message}")
    if ERRORS:
        print("\nFAIL")
        for message in ERRORS:
            print(f"- {message}")
        return 1
    print("\nPASS: skill package is internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
