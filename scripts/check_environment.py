#!/usr/bin/env python3
"""Probe this machine for what the skill can actually do, and what to install.

Run this before promising a deliverable. The skill can produce a renderer-neutral
brief and manifest with nothing installed, but rendering, checkpoint evidence, and
final-state comparison each need a specific tool, and an agent that discovers a
missing dependency by hitting an error mid-task either stalls or degrades silently.

The probe reports four states per capability:

    ok           available and usable now
    degraded     available, but a documented feature is lost
    missing      not installed, with the exact install command
    blocked      not installable here, and what to do instead

It never installs anything and never writes outside stdout.

Usage:
    python scripts/check_environment.py
    python scripts/check_environment.py --json
    python scripts/check_environment.py --mode produce
    python scripts/check_environment.py --self-test
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

OK = "ok"
DEGRADED = "degraded"
MISSING = "missing"
BLOCKED = "blocked"

MIN_PYTHON = (3, 10)
MIN_DISK_GB_PRODUCE = 10
MIN_DISK_GB_4K = 40

# Install commands are per-platform. Every entry must be copy-pasteable and must
# not assume a package manager the machine does not have.
INSTALL = {
    "pillow": {
        "pip": "python -m pip install \"Pillow>=9.0\"",
        "pipx": "pipx install Pillow",
        "dnf": "sudo dnf install python3-pillow",
        "brew": "brew install python-pillow",
        "apt": "sudo apt-get install python3-pil",
        "win": "python -m pip install \"Pillow>=9.0\"",
    },
    "numpy": {
        "pip": "python -m pip install \"numpy>=1.23\"",
        "dnf": "sudo dnf install python3-numpy",
        "brew": "brew install numpy",
        "apt": "sudo apt-get install python3-numpy",
        "win": "python -m pip install \"numpy>=1.23\"",
    },
    "scipy": {
        "pip": "python -m pip install \"scipy>=1.9\"",
        "dnf": "sudo dnf install python3-scipy",
        "brew": "brew install scipy",
        "apt": "sudo apt-get install python3-scipy",
        "win": "python -m pip install \"scipy>=1.9\"",
    },
    "ffmpeg": {
        "dnf": "sudo dnf install ffmpeg",
        "brew": "brew install ffmpeg",
        "apt": "sudo apt-get install ffmpeg",
        "win": "winget install Gyan.FFmpeg",
        "conda": "conda install -c conda-forge ffmpeg",
        "note": "FFmpeg is the only hard external dependency for checkpoint evidence. On Fedora it comes from RPM Fusion rather than the default repositories.",
    },
    "node": {
        "dnf": "sudo dnf install nodejs",
        "brew": "brew install node",
        "apt": "sudo apt-get install -y nodejs npm",
        "win": "winget install OpenJS.NodeJS.LTS",
        "note": "Node 18 or newer is required by Remotion.",
    },
    "remotion": {
        "npm": "npm install remotion @remotion/cli",
        "npx": "npx remotion studio",
        "note": "Remotion renders in headless Chrome, so a Chrome or Chromium binary "
                "must also be available. Licensing is per-company; verify before "
                "commercial delivery.",
    },
    "rsvg": {
        "brew": "brew install librsvg",
        "apt": "sudo apt-get install librsvg2-bin",
        "dnf": "sudo dnf install librsvg2-tools",
        "win": "winget install GNOME.GLib",
        "note": "rsvg-convert is one rung of the renderer ladder. Without root, "
                "extract the package to ~/.local and add it to PATH: "
                "dnf download librsvg2-tools && rpm2cpio <pkg> | (cd ~/.local/rsvg && cpio -idm)",
    },
    "potrace": {
        "dnf": "sudo dnf install potrace",
        "brew": "brew install potrace",
        "apt": "sudo apt-get install potrace",
        "note": "Only needed to vectorize a flattened raster. Prefer an approved "
                "vector source over tracing.",
    },
}

# mode -> capabilities that must not be `missing`
MODE_REQUIREMENTS = {
    "audit": [],
    "plan": [],
    "produce": ["pillow", "numpy", "ffmpeg"],
    "interactive": ["node"],
}

# A mode can be satisfied by any one of several alternatives. `produce` needs a
# renderer, and there is more than one rung: Remotion needs node, the per-frame
# SVG rung needs rsvg-convert. Requiring node outright would report a machine
# that can render as blocked, which is the wrong answer.
MODE_ANY_REQUIREMENTS = {
    "produce": (["node", "rsvg"], "a renderer: Remotion (node) or rsvg-convert (rsvg)"),
}


def platform_key() -> str:
    """The package manager this machine actually has.

    Assuming apt on every Linux prints a command that cannot work on Fedora,
    openSUSE, or Arch, and a wrong install command is worse than none because
    it looks authoritative. Each manager is detected by its binary on PATH.
    """
    system = platform.system()
    if system == "Darwin":
        return "brew"
    if system == "Windows":
        return "win"
    if system == "Linux":
        for binary, key in (("dnf", "dnf"), ("apt-get", "apt"), ("pacman", "pacman"),
                            ("zypper", "zypper"), ("apk", "apk")):
            if shutil.which(binary):
                return key
        return "apt"
    return "pip"



def install_hint(capability: str) -> list[str]:
    entry = INSTALL.get(capability)
    if not entry:
        return []
    # Only this machine's package manager is offered. Another distro's manager
    # is not a fallback, it is a command that will fail, so it never appears.
    # Language-level managers are cross-platform and are safe fallbacks.
    order = [platform_key(), "pip", "npm", "npx", "conda", "pipx"]
    hints, seen = [], set()
    for key in order:
        value = entry.get(key)
        if value and key not in seen:
            seen.add(key)
            hints.append(value)
    return hints


def check_python() -> dict:
    version = sys.version_info
    ok = (version.major, version.minor) >= MIN_PYTHON
    return {
        "capability": "python",
        "state": OK if ok else BLOCKED,
        "detail": f"{version.major}.{version.minor}.{version.micro} on "
                  f"{platform.system()} {platform.machine()}",
        "requires": f">= {'.'.join(str(n) for n in MIN_PYTHON)}",
        "needed_for": "every utility in this package",
        "install": [] if ok else ["install Python 3.10 or newer from python.org"],
    }


def check_module(name: str, capability: str, needed_for: str, absent_note: str = "") -> dict:
    """`absent_note` says what is lost when the module is NOT installed.

    It must not downgrade a present module to `degraded`: an installed optional
    dependency is `ok`, and the note only matters on the `missing` path.
    """
    spec = importlib.util.find_spec(name)
    if spec is None:
        return {"capability": capability, "state": MISSING, "detail": "not installed",
                "needed_for": needed_for, "degrades": absent_note,
                "install": install_hint(capability)}
    version = ""
    try:
        version = getattr(__import__(name), "__version__", "") or ""
    except Exception:
        version = "installed"
    return {"capability": capability, "state": OK,
            "detail": f"version {version}" if version else "installed",
            "needed_for": needed_for, "degrades": "", "install": []}


def tool_version(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=8)
        line = (result.stdout or result.stderr or "").strip().splitlines()
        return line[0][:80] if line else "installed"
    except (subprocess.TimeoutExpired, OSError):
        return "installed"


ROOTLESS_DIRS = [
    Path.home() / ".local" / "rsvg" / "usr" / "bin",
    Path.home() / ".local" / "bin",
    Path.home() / "bin",
]


def which_tool(tool: str) -> str | None:
    """`shutil.which` plus the locations a no-root install lands in.

    A package extracted without sudo does not reach the default PATH, so a tool
    that is genuinely installed would otherwise be reported missing. That is the
    difference between a blocked verdict and an honest `degraded` one.
    """
    found = shutil.which(tool)
    if found:
        return found
    for directory in ROOTLESS_DIRS:
        candidate = directory / tool
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def check_tool(tool: str, capability: str, needed_for: str, probe: list[str] | None = None,
               absent_note: str = "", install_key: str | None = None) -> dict:
    """`install_key` lets a capability share another one's install command, which
    is how ffprobe is reported under its own name but installed as part of ffmpeg."""
    path = which_tool(tool)
    if not path:
        return {"capability": capability, "state": MISSING, "detail": "not on PATH",
                "needed_for": needed_for, "degrades": absent_note,
                "install": install_hint(install_key or capability)}
    return {"capability": capability, "state": OK,
            "detail": f"{path} ({tool_version(probe)})" if probe else path,
            "needed_for": needed_for, "degrades": "", "install": []}


def check_disk() -> dict:
    try:
        free_gb = shutil.disk_usage(str(Path(__file__).resolve().parent)).free // (1024 ** 3)
    except OSError:
        return {"capability": "disk", "state": DEGRADED, "detail": "could not measure",
                "needed_for": "render output and intermediate files",
                "degrades": "cannot warn before a render fills the volume"}
    state = OK if free_gb >= MIN_DISK_GB_PRODUCE else DEGRADED
    detail = f"{free_gb} GB free"
    if free_gb < MIN_DISK_GB_4K:
        detail += f"; below {MIN_DISK_GB_PRODUCE} GB for SD and {MIN_DISK_GB_4K} GB for 4K"
    return {"capability": "disk", "state": state, "detail": detail,
            "needed_for": "render output, checkpoints, and intermediates",
            "degrades": "" if state == OK else "a render may fail part-way through",
            "install": []}


def check_hardware() -> dict:
    cores = os.cpu_count() or 1
    notes = []
    if cores <= 2:
        notes.append("one or two cores will make a Remotion render slow enough that "
                     "the agent should tell the user before starting one")
    return {"capability": "hardware", "state": DEGRADED if notes else OK,
            "detail": f"{cores} logical cores",
            "needed_for": "parallel per-frame rendering",
            "degrades": "; ".join(notes),
            "note": "The skill does not probe the GPU. Browser-decode performance is a "
                    "viewer-device question, not a producer-machine one; read "
                    "references/delivery/digital-product-and-ui.md.",
            "install": []}


def check_remotion() -> dict:
    """Remotion needs Node plus a Chrome binary, and both must be present."""
    node = shutil.which("node")
    if not node:
        return {"capability": "remotion", "state": MISSING,
                "detail": "Node not found; Remotion cannot run",
                "needed_for": "frame-driven video rendering",
                "install": install_hint("node") + install_hint("remotion")}
    result = {"capability": "remotion", "state": DEGRADED, "needed_for":
              "frame-driven video rendering", "install": install_hint("remotion")}
    try:
        version = subprocess.run(["node", "--version"], capture_output=True, text=True,
                                 timeout=8).stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        version = "unknown"
    major = 0
    if version.startswith("v"):
        try:
            major = int(version[1:].split(".")[0])
        except ValueError:
            major = 0
    if major and major < 18:
        result["state"] = BLOCKED
        result["detail"] = f"Node {version} is older than the required 18"
        result["degrades"] = ("Remotion will not install; use the SVG, Lottie, or "
                              "After Effects path instead")
        return result
    chrome = any(shutil.which(name) for name in
                 ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"))
    if chrome:
        result["state"] = OK
        result["detail"] = f"Node {version} and a Chrome binary are present"
    else:
        result["detail"] = f"Node {version} present, no Chrome binary found"
        result["degrades"] = ("Remotion downloads its own headless Chrome on first run; "
                              "if the machine is offline or locked down, rendering is blocked")
    return result


def probe_all() -> list:
    return [
        check_python(),
        check_module("PIL", "pillow", "raster profiling and final-frame comparison"),
        check_module("numpy", "numpy", "raster profiling and final-frame comparison"),
        check_module("scipy", "scipy",
                     "connected components, hole detection, and stroke-width metrics",
                     "the profiler reports component and hole metrics as null and "
                     "lowers confidence rather than guessing"),
        check_tool("ffmpeg", "ffmpeg", "checkpoint contact sheets and frame extraction"),
        check_tool("ffprobe", "ffprobe", "stream metadata for delivery checks",
                   probe=["ffprobe", "-version"],
                   absent_note="stream metadata checks are unavailable; frame "
                               "extraction still works with ffmpeg alone",
                   install_key="ffmpeg"),
        check_remotion(),
        check_tool("rsvg-convert", "rsvg",
                   "per-frame SVG rasterisation for the rsvg + ffmpeg rung",
                   probe=["rsvg-convert", "--version"],
                   absent_note="the rsvg + ffmpeg renderer rung is unavailable; render "
                               "with Remotion instead, or agree a lower-fidelity rung"),
        check_tool("potrace", "potrace", "vectorizing a flattened raster",
                   absent_note="a flattened raster stays flattened; ask for a vector "
                               "source rather than tracing"),
        check_disk(),
        check_hardware(),
    ]


def mode_verdict(capabilities: list, mode: str) -> dict:
    required = MODE_REQUIREMENTS.get(mode, [])
    by_name = {item["capability"]: item for item in capabilities}
    unmet, degraded = [], []
    for name in required:
        item = by_name.get(name)
        if not item:
            continue
        if item["state"] == MISSING:
            unmet.append(name)
        elif item["state"] in (DEGRADED, BLOCKED):
            degraded.append(name)
    # Any-of group: satisfied when one alternative is OK. A degraded alternative
    # does not fail the mode as long as another one works, because that is the
    # whole point of having two renderer rungs.
    alternatives, label = MODE_ANY_REQUIREMENTS.get(mode, ([], ""))
    if alternatives:
        states = [by_name.get(name, {}).get("state") for name in alternatives]
        if OK not in states:
            unmet.append(label)
    if unmet:
        verdict = "blocked"
    elif degraded:
        verdict = "degraded"
    else:
        verdict = "ok"
    return {"mode": mode, "verdict": verdict, "missing": unmet, "degraded": degraded,
            "fallback": ("Complete the renderer-neutral brief and manifest in "
                         "assets/motion-manifest-template.json, mark rendering "
                         "`blocked`, and list the missing installs above."
                         if verdict != "ok" else None)}


def self_test() -> int:
    failures = []
    capabilities = probe_all()
    if not capabilities:
        failures.append("probe returned no capabilities")
    names = {item["capability"] for item in capabilities}
    for required in ("python", "pillow", "numpy", "scipy", "ffmpeg", "ffprobe",
                     "remotion", "rsvg", "potrace", "disk", "hardware"):
        if required not in names:
            failures.append(f"probe did not report '{required}'")
    for item in capabilities:
        if item["state"] not in (OK, DEGRADED, MISSING, BLOCKED):
            failures.append(f"{item['capability']} has an invalid state {item['state']!r}")
        if item["state"] == MISSING and not item.get("install"):
            failures.append(f"{item['capability']} is missing but reports no install hint")
    for mode in MODE_REQUIREMENTS:
        verdict = mode_verdict(capabilities, mode)
        if verdict["verdict"] not in ("ok", "degraded", "blocked"):
            failures.append(f"mode {mode} produced an invalid verdict")
    if failures:
        print("FAIL: environment probe self-test", file=sys.stderr)
        for message in failures:
            print(f"- {message}", file=sys.stderr)
        return 1
    counts = {}
    for item in capabilities:
        counts[item["state"]] = counts.get(item["state"], 0) + 1
    print(f"note: probed {len(capabilities)} capabilities: "
          + ", ".join(f"{count} {state}" for state, count in sorted(counts.items())))
    print("\nPASS: environment probe self-test")
    return 0


def render_text(capabilities: list, verdicts: list) -> str:
    order = {OK: 0, DEGRADED: 1, MISSING: 2, BLOCKED: 3}
    lines = ["", "Brand motion skill - environment probe", "=" * 60, ""]
    for item in sorted(capabilities, key=lambda i: (order[i["state"]], i["capability"])):
        mark = {OK: "[ ok ]", DEGRADED: "[warn]", MISSING: "[miss]", BLOCKED: "[BLOCK]"}[item["state"]]
        lines.append(f"{mark} {item['capability']:<12} {item['detail']}")
        if item.get("degrades"):
            lines.append(f"             loses: {item['degrades']}")
        if item["state"] in (MISSING, BLOCKED) and item.get("install"):
            lines.append(f"             install: {item['install'][0]}")
    lines += ["", "Task modes", "-" * 60]
    for verdict in verdicts:
        lines.append(f"  {verdict['mode']:<12} {verdict['verdict'].upper()}")
        if verdict["missing"]:
            lines.append(f"               missing: {', '.join(verdict['missing'])}")
        if verdict["fallback"]:
            lines.append(f"               {verdict['fallback']}")
    lines += ["", "Full detail: python scripts/check_environment.py --json", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe this machine for what the brand motion skill can do.")
    parser.add_argument("--json", action="store_true", help="emit the full report as JSON")
    parser.add_argument("--mode", default="produce", choices=sorted(MODE_REQUIREMENTS),
                        help="task mode to report a verdict for (default produce)")
    parser.add_argument("--self-test", action="store_true",
                        help="run the dependency-free smoke test and exit")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    capabilities = probe_all()
    verdicts = [mode_verdict(capabilities, mode) for mode in sorted(MODE_REQUIREMENTS)]
    if args.json:
        print(json.dumps({
            "platform": f"{platform.system()} {platform.machine()}",
            "python": platform.python_version(),
            "capabilities": capabilities,
            "modes": verdicts,
            "install_hint": "Nothing was installed. Run the printed commands yourself.",
        }, indent=2))
        return 0
    print(render_text(capabilities, verdicts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
