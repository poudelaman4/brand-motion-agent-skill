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

import ast
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


def resolves(rel: str, source: Path) -> bool:
    """Does a backticked path resolve from any convention this package uses?

    Three conventions are in use and all three are correct in context:
    root-relative from SKILL.md, references-relative from a reference file
    (siblings drop the `references/` prefix per the house rule), and
    sibling-relative for a path in the same directory.
    """
    candidates = [ROOT / rel, ROOT / "references" / rel, source.parent / rel]
    if rel.startswith("references/") and rel.count("/") == 1:
        candidates.append(source.parent / Path(rel).name)
    return any(candidate.exists() for candidate in candidates)


def check_backtick_paths(body: str) -> None:
    seen: set[str] = set()
    for match in BACKTICK_PATH_RE.finditer(body):
        rel = match.group(1)
        if "/" not in rel:
            continue
        if rel in seen:
            continue
        seen.add(rel)
        if not resolves(rel, ROOT / "SKILL.md"):
            fail(f"SKILL.md references '{rel}' but the path does not exist.")
    if seen:
        note(f"checked {len(seen)} referenced file paths in SKILL.md.")


def check_reference_paths() -> None:
    """Backticked paths inside references must resolve too.

    A reference is loaded on demand, so a broken path inside one is invisible
    until an agent tries to follow it. Guard the whole package, not just the
    file that is always loaded.
    """
    checked = unresolved = 0
    for path in sorted((ROOT / "references").rglob("*.md")):
        for match in BACKTICK_PATH_RE.finditer(path.read_text(encoding="utf-8")):
            rel = match.group(1)
            if "/" not in rel or rel.startswith(("http", "#")):
                continue
            checked += 1
            if not resolves(rel, path):
                unresolved += 1
                fail(f"{path.relative_to(ROOT)} references '{rel}' but the path does "
                     "not resolve from the skill root, from references/, or from its "
                     "own directory.")
    note(f"checked {checked} backticked paths across references/, {unresolved} unresolved.")


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


MAX_BODY_LINES = 500      # agentskills.io specification guidance
MAX_BODY_TOKENS = 5000    # agentskills.io progressive-disclosure guidance


def check_body_budget() -> None:
    """Fail when SKILL.md outgrows the specification's guidance.

    The specification loads the whole body on activation, so an oversized
    SKILL.md is paid for on every task. The fix is to route to a reference,
    not to keep appending, so this fails rather than advises.
    """
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    body = text[match.end():] if match else text
    lines = len(body.splitlines())
    tokens = len(body) // 4
    if lines > MAX_BODY_LINES:
        fail(f"SKILL.md body is {lines} lines; the guidance is under {MAX_BODY_LINES}. "
             "Move detail into references/ and route to it.")
    if tokens > MAX_BODY_TOKENS:
        fail(f"SKILL.md body is about {tokens} tokens; the guidance is under "
             f"{MAX_BODY_TOKENS}. Move detail into references/ and route to it.")
    note(f"SKILL.md body is {lines} lines and about {tokens} tokens, against guidance "
         f"of {MAX_BODY_LINES} lines and {MAX_BODY_TOKENS} tokens.")


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


def check_environment_probe() -> None:
    """The probe must run clean and agree with itself.

    A probe that cannot detect its own breakage is worse than no probe, so this
    runs it and cross-checks the mode verdicts against the capability states.
    """
    script = ROOT / "scripts" / "check_environment.py"
    if not script.exists():
        fail("scripts/check_environment.py is missing.")
        return
    result = subprocess.run([sys.executable, str(script), "--self-test"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"environment probe self-test failed: "
             f"{result.stderr.strip() or result.stdout.strip()}")
        return
    report = subprocess.run([sys.executable, str(script), "--json"],
                            capture_output=True, text=True)
    if report.returncode != 0:
        fail(f"environment probe --json failed: {report.stderr.strip()}")
        return
    try:
        document = json.loads(report.stdout)
    except json.JSONDecodeError as exc:
        fail(f"environment probe did not emit valid JSON: {exc}")
        return
    states = {item["capability"]: item["state"] for item in document.get("capabilities", [])}
    if len(states) != len(document.get("capabilities", [])):
        fail("environment probe reported a capability name twice.")
    for mode in document.get("modes", []):
        verdict = mode.get("verdict")
        if verdict == "ok" and any(states.get(name) == "missing"
                                   for name in mode.get("missing", []) or []):
            fail(f"mode {mode.get('mode')} is ok but lists missing capabilities.")
    note(f"environment probe reports {len(states)} capabilities across "
         f"{len(document.get('modes', []))} task modes.")


def check_pipeline_integration() -> None:
    """Run a real logo through the pipeline and assert the documented outcome.

    Every other check tests one piece. This is the only one that tests whether
    they compose: profile, rank, taste, and re-read. It pins the behaviours
    `references/worked-example.md` documents, so the example cannot drift into
    describing something the scripts no longer do.
    """
    fixture = ROOT / "evals" / "files" / "layered-mark.svg"
    if not fixture.exists():
        fail("evals/files/layered-mark.svg is missing; the worked example has no source.")
        return
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "profile_logo.py"), str(fixture),
         "--register", "premium", "--frequency", "occasional", "--draw-plan"],
        capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"pipeline profiling run failed: {result.stderr.strip()}")
        return
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"pipeline run did not emit valid JSON: {exc}")
        return

    profile = document.get("profile", {})
    recommendation = document.get("recommendation", {})
    taste = recommendation.get("taste", {}) or {}

    # The example's central claim: the register vetoes the highest raw score.
    permitted = taste.get("permitted") or []
    vetoed = [item.get("technique") for item in taste.get("vetoed") or []]
    if "separation_explode" not in vetoed:
        fail("taste gate did not veto separation_explode for the premium register; "
             "the worked example describes a gate that no longer fires.")
    if "separation_explode" in permitted:
        fail("a vetoed technique is still listed as permitted; a veto must remove "
             "rather than demote.")
    primary = (recommendation.get("primary") or {}).get("technique")
    if primary != "mask_wipe":
        fail(f"expected mask_wipe as primary after the veto, got {primary!r}.")

    # Live text must gate all three families the example names.
    blocked = {item.get("technique") for item in recommendation.get("blocked") or []}
    for technique in ("kinetic_typography", "line_draw_on", "multi_stroke_trace"):
        if technique not in blocked:
            fail(f"{technique} is no longer gated by live text; gate code LIVE_TEXT "
                 "should block it, and the worked example says so.")

    # Budgets are ceilings, and the palette is the brand colour source.
    budget = taste.get("budget") or {}
    if budget.get("duration_ceiling_s") != 0.96:
        fail(f"premium x occasional duration ceiling changed to "
             f"{budget.get('duration_ceiling_s')!r}; the worked example quotes 0.96 s.")
    if budget.get("overshoot_ceiling") != 0.0:
        fail("the premium register no longer enforces zero overshoot.")
    palette = profile.get("palette") or []
    if not palette or not str(palette[0].get("hex", "")).startswith("#"):
        fail("the profile no longer reports a palette, so the delivery files that "
             "ask for the brand colour have no source for it.")

    note("pipeline integration: profile, rank, taste veto, live-text gating, and "
         "palette all agree with references/worked-example.md.")


def _pull_brace_object(source: str, name: str):
    """Return the first `{...}` literal assigned to `name`, as a dict."""
    match = re.search(rf"{name}\s*[:=]\s*", source)
    if not match:
        return None
    start = source.index("{", match.end())
    depth = 0
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return ast.literal_eval(re.sub(r"#.*", "", source[start:index + 1]))
                except (ValueError, SyntaxError):
                    return None
    return None


def check_taste_tables_agree() -> None:
    """The taste ceilings live in three places; assert they are the same numbers.

    The profiler has its own register and frequency tables, the manifest
    validator has a second copy it uses to reject a hand-edited budget, and
    `assets/motion-tokens.json` is the documented source of both. Nothing else
    keeps them aligned. If they drift, the profiler emits a budget the validator
    refuses, and a correct workflow deadlocks on a number nobody chose.

    This is the check that would have caught it.
    """
    try:
        tokens = json.loads((ROOT / "assets" / "motion-tokens.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"assets/motion-tokens.json could not be read: {exc}")
        return
    profiler = (ROOT / "scripts" / "profile_logo.py").read_text()
    validator = (ROOT / "scripts" / "validate_motion_spec.py").read_text()

    profiler_registers = _pull_brace_object(profiler, "REGISTERS") or {}
    validator_registers = _pull_brace_object(validator, "REGISTER_BUDGET_CEILINGS") or {}
    profiler_frequencies = _pull_brace_object(profiler, "FREQUENCIES") or {}
    validator_frequencies = _pull_brace_object(validator, "FREQUENCY_FACTORS") or {}
    token_registers = tokens.get("registers", {})
    token_frequencies = tokens.get("frequencies", {})

    reg_keys = ("max_duration_s", "max_gestures", "max_overshoot")
    for name, spec in token_registers.items():
        expected = tuple(spec.get(key) for key in reg_keys)
        seen = {
            "profiler": tuple((profiler_registers.get(name) or {}).get(key) for key in reg_keys),
            "validator": tuple(validator_registers.get(name)),
            "tokens": expected,
        }
        if len(set(seen.values())) != 1:
            fail(f"register '{name}' disagrees across copies: "
                 + "; ".join(f"{k}={v}" for k, v in seen.items()))
    for name in set(profiler_registers) | set(validator_registers):
        if name not in token_registers:
            fail(f"register '{name}' exists in a script table but not in motion-tokens.json.")

    freq_keys = ("duration_factor", "gesture_factor", "overshoot_factor")
    for name, spec in token_frequencies.items():
        p = profiler_frequencies.get(name)
        v = validator_frequencies.get(name)
        pv = tuple(p.get(key) for key in freq_keys) if isinstance(p, dict) else tuple(p or ())
        vv = tuple(v.get(key) for key in freq_keys) if isinstance(v, dict) else tuple(v or ())
        tv = tuple(spec.get(key) for key in freq_keys)
        if len({pv, vv, tv}) != 1:
            fail(f"frequency '{name}' disagrees across copies: "
                 f"profiler={pv} validator={vv} tokens={tv}")

    note(f"taste tables agree across profiler, validator, and motion-tokens.json "
         f"({len(token_registers)} registers, {len(token_frequencies)} frequencies).")


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
    check_reference_paths()
    check_body_budget()
    check_schema()
    check_evals()
    check_manifest_validator()
    check_profiler()
    check_volatile_figures()
    check_environment_probe()
    check_pipeline_integration()
    check_taste_tables_agree()

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
