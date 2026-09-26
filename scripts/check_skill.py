#!/usr/bin/env python3
"""Fast, dependency-free self-check for the animation-logo-skill package.

Validates the skill without needing Pillow/NumPy/SciPy/FFmpeg so it can run in
CI or as a pre-commit sanity gate. It checks:

- SKILL.md frontmatter: required keys, name matches the directory, and description
  length.
- Referenced relative paths in backticks inside SKILL.md exist.
- Eval fixture files referenced by the evaluation cases point at real paths.
- schemas/motion-spec.schema.json parses and has a sane root.
- scripts/profile_logo.py passes its dependency-free self-test.
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
STAMP_DATE = "2026-09-26"  # release date for the volatile-figure stamps
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
    advanced = ROOT / "evals" / "files" / "valid-advanced-spec.json"
    if not advanced.exists():
        fail("expected file missing for validator smoke test: evals/files/valid-advanced-spec.json")
    else:
        result = subprocess.run([sys.executable, str(script), str(advanced)],
                                capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"valid-advanced-spec.json should PASS but returned {result.returncode}: "
                 f"{result.stdout.strip()}")
        else:
            note("advanced manifest validates, so the stroke, separation, mask, and "
                 "detection channels stay exercised.")
    # The shipped template is what an agent copies from. If it drifts out of the
    # contract, every manifest produced from it is wrong, so validate it too.
    template = ROOT / "assets" / "motion-manifest-template.json"
    if not template.exists():
        fail("assets/motion-manifest-template.json is missing.")
    else:
        result = subprocess.run([sys.executable, str(script), str(template)],
                                capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"the shipped manifest template must satisfy the contract but returned "
                 f"{result.returncode}: {result.stdout.strip()}")
        else:
            note("the shipped manifest template satisfies the current contract.")
    bad = subprocess.run([sys.executable, str(script), str(invalid)], capture_output=True, text=True)
    if bad.returncode == 0:
        fail("invalid-motion-spec.json should FAIL but the validator passed it.")
    else:
        note("manifest validator correctly passes the valid fixture and rejects the invalid one.")


VOLATILE_FILES = {
    "references/delivery/social-and-editorial.md": STAMP_DATE,
    "references/delivery/digital-product-and-ui.md": STAMP_DATE,
}


def check_volatile_figures() -> None:
    """Volatile platform figures must carry a verified-on date.

    These numbers change whenever a platform ships, so a row with no date cannot be
    distinguished from a row that was accurate when it was written. This only
    checks that the date is present and not absurd; expiry is a judgement call
    made per campaign, and the files say so.
    """
    import datetime

    today = datetime.date.today()
    for rel, expected in sorted(VOLATILE_FILES.items()):
        path = ROOT / rel
        if not path.exists():
            fail(f"expected volatile-figure file missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if "Verified on" not in text:
            fail(f"{rel} holds volatile platform figures with no 'Verified on' column.")
            continue
        stamps = re.findall(r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|", text)
        if not stamps:
            fail(f"{rel} has a 'Verified on' header but no dated rows.")
            continue
        try:
            newest = max(datetime.date.fromisoformat(stamp) for stamp in stamps)
        except ValueError as exc:
            fail(f"{rel} has a malformed verified-on date: {exc}")
            continue
        age_days = (today - newest).days
        if newest != datetime.date.fromisoformat(expected):
            note(f"{rel} verified-on is {newest}, not the package release date {expected}.")
        if age_days > 90:
            fail(f"{rel} volatile figures were verified {age_days} days ago; past the "
                 "90-day horizon. Re-verify the platform zones or mark them blocked.")
        else:
            note(f"{rel} volatile figures verified {age_days} days ago.")


def check_profiler() -> None:
    script = ROOT / "scripts" / "profile_logo.py"
    fixture = ROOT / "evals" / "files" / "layered-mark.svg"
    for path in (script, fixture):
        if not path.exists():
            fail(f"expected file missing for profiler smoke test: {path.relative_to(ROOT)}")
    if not (script.exists() and fixture.exists()):
        return
    result = subprocess.run([sys.executable, str(script), "--self-test"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"profiler self-test failed: {result.stderr.strip() or result.stdout.strip()}")
    else:
        note("profiler self-test passes on the layered vector fixture.")
    # The taste gate is a veto, not a preference, so it has to be exercised too.
    gated = subprocess.run(
        [sys.executable, str(script), str(fixture), "--register", "luxury",
         "--frequency", "daily", "--json"],
        capture_output=True, text=True)
    if gated.returncode != 0:
        fail(f"profiler taste gate failed: {gated.stderr.strip() or gated.stdout.strip()}")
        return
    try:
        document = json.loads(gated.stdout)
    except json.JSONDecodeError as exc:
        fail(f"profiler taste gate did not emit valid JSON: {exc}")
        return
    taste = document.get("recommendation", {}).get("taste", {})
    budget = taste.get("budget", {})
    # luxury at daily frequency: 1.5 s ceiling scaled by 0.5, one gesture, zero overshoot.
    if budget.get("duration_ceiling_s") != 0.75 or budget.get("gesture_ceiling") != 1 \
            or budget.get("overshoot_ceiling") != 0.0:
        fail(f"taste budget is wrong for luxury at daily frequency: {budget}")
    else:
        note("taste gate applies the register veto and the frequency-scaled budget.")


def main() -> int:
    front, body = load_skill_md()
    check_frontmatter(front)
    check_backtick_paths(body)
    check_schema()
    check_evals()
    check_manifest_validator()
    check_profiler()
    check_volatile_figures()

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
