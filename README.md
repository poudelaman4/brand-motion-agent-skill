# Brand Motion Agent Skill (`logo-motion-guardrail`)

[![Repository](https://img.shields.io/badge/Repository-poudelaman4%2Fbrand--motion--agent--skill-111827)](https://github.com/poudelaman4/brand-motion-agent-skill)
[![Open Agent Skills](https://img.shields.io/badge/Open%20Agent%20Skills-schema-4B8B3B)](https://agentskills.io/specification)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code%20Skill-supported-6E56CF)](https://code.claude.com/docs/en/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981)](https://opensource.org/licenses/MIT)

Listed on mcpservers.org

[![Listed on mcpservers.org](https://mcpservers.org/badge.svg)](https://mcpservers.org/servers/poudelaman4/brand-motion-agent-skill)

A **brand-safe logo animation agent skill**. It teaches a filesystem-enabled coding
agent (Claude Code, Open Code, Cursor, and others) to animate an *already approved*
logo without redrawing it: preserve canonical geometry and the final lockup, keep the
motion restrained and brand-appropriate, and be honest about what the source can and
cannot support. It produces renderer-neutral motion briefs and manifests and hands
off to Remotion, SVG, Lottie/dotLottie, After Effects, FFmpeg, or MLT/Kdenlive.

> **Maintainer and creator:** **Aman Paudel** — GitHub: [poudelaman4](https://github.com/poudelaman4)
>
> **Repository:** https://github.com/poudelaman4/brand-motion-agent-skill
> **Installed skill ID:** `animation-logo-skill` · **Runtime:** local, filesystem-enabled, deterministic, renderer-neutral

## Discovery keywords

`brand-safe logo animation agent skill` · `Claude Code skill` · `Open Agent Skills schema` · `MLT video automation framework` · logo reveal automation · brand identity protection · canonical geometry validation · SVG logo animation · Lottie logo reveal · dotLottie state machine · Remotion logo animation · transparent logo video · white-background logo animation · AI motion design QA

This README uses explicit headings, tables, code blocks, installation paths, task modes, and terminology so AI indexers, LLM scrapers, and Google SEO can identify the repository accurately without relying on hidden context.

## What this is

A reusable **agent skill package**, not a video editor or renderer. It teaches an agent how to:

- Audit vector, layered-raster, flattened-raster, and live-text logo sources.
- Protect approved geometry, wordmarks, counters, clear space, colors, and alpha behavior.
- Classify the logo, narrative motion, context, runtime, background, and platform.
- Choose a restrained pattern for botanical, geometric, monogram, wordmark, badge, education, premium, playful, wellness, or technology identities.
- Create a motion brief, frame-accurate manifest, reduced-motion state, and QA plan.
- Produce renderer-neutral handoffs or implement a supported renderer when one is available.
- Inspect encoded frames, build exact checkpoint sheets, and compare final states with documented tolerances.
- Validate extracted raster transitions at direct start/mid/end stills and in decoded output before delivery.

Generative video is never allowed to silently redraw an approved logo. When a flattened source does not contain semantic layers, the skill reports the limitation and offers a grouped or whole-mark fallback instead of inventing hidden pixels.

## Repository layout

```text
brand-motion-agent-skill/
├── SKILL.md                         # Agent instructions and task modes
├── README.md                        # This document
├── LICENSE                          # MIT license
├── requirements.txt                 # Optional Python inspection/QA utilities
├── assets/
│   ├── motion-brief-template.json   # Creative and approval brief
│   ├── motion-manifest-template.json# Executable motion contract
│   └── motion-tokens.json           # Timing, easing, and overshoot tokens
├── schemas/
│   └── motion-spec.schema.json      # JSON Schema for motion manifests
├── scripts/
│   ├── inspect_logo_assets.py       # Alpha and diagnostic component inspection
│   ├── validate_motion_spec.py      # Manifest validation
│   ├── make_checkpoint_contact_sheet.py
│   ├── compare_final_frame.py       # Encoded final-state comparison
│   └── check_skill.py               # Dependency-free self-check of this package
├── references/
│   ├── patterns/                    # Organic, geometric, monogram, wordmark, badge
│   ├── contexts/                    # Education/LMS, premium, playful, tech, wellness
│   ├── delivery/                    # Backgrounds, alpha, codecs, accessibility
│   ├── implementation/              # Remotion, vector/Lottie, AE, flattened raster
│   └── qa/                          # Checklist, manifest contract, failure catalog
└── evals/                           # Development prompts and fixtures
```

## Prerequisites

Required for the core skill format:

- Git
- A filesystem-enabled AI coding agent
- Python 3.10+ for the bundled utilities

Recommended for production rendering and QA:

- FFmpeg and FFprobe
- Node.js and a renderer such as Remotion
- An SVG editor or vector source for independent logo motion
- Kdenlive/MLT for editorial timeline assembly
- A browser/runtime test target for SVG, Lottie, or dotLottie output

The agent can still operate in **Plan** or **Audit** mode when a renderer, FFmpeg, or source layers are unavailable. It should mark rendering or independent layer motion as `BLOCKED` rather than guessing.

## Installation

### 1. Clone the repository

The repository name and the installed skill ID are intentionally different. The Open Agent Skills specification requires the directory containing `SKILL.md` to match the `name` in frontmatter, so install the repository **as `animation-logo-skill`**:

```bash
set -euo pipefail

REPO_URL="https://github.com/poudelaman4/brand-motion-agent-skill.git"
SKILL_ID="animation-logo-skill"
INSTALL_ROOT="${HOME}/.agents/skills"
SKILL_DIR="${INSTALL_ROOT}/${SKILL_ID}"

mkdir -p "${INSTALL_ROOT}"

if [ -d "${SKILL_DIR}/.git" ]; then
  git -C "${SKILL_DIR}" pull --ff-only
else
  git clone "${REPO_URL}" "${SKILL_DIR}"
fi

printf 'Installed skill: %s\n' "${SKILL_DIR}"
```

The universal `~/.agents/skills` location is discoverable by Open Code and is also compatible with agents that follow the Agent Skills convention. Claude Code has an additional native location described below.

### 2. Install optional Python dependencies

Use a virtual environment so the skill does not modify the system Python installation:

```bash
set -euo pipefail
SKILL_DIR="${HOME}/.agents/skills/animation-logo-skill"

cd "${SKILL_DIR}"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell equivalent:

```powershell
$SkillDir = "$HOME\.agents\skills\animation-logo-skill"
Set-Location $SkillDir
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Verify the installation

```bash
set -euo pipefail
SKILL_DIR="${HOME}/.agents/skills/animation-logo-skill"

test -f "${SKILL_DIR}/SKILL.md"
python3 "${SKILL_DIR}/scripts/validate_motion_spec.py" \
  "${SKILL_DIR}/evals/files/valid-motion-spec.json" \
  --check-files

command -v git
command -v python3
command -v ffmpeg || true
command -v ffprobe || true
```

If the public repository is not yet visible, authenticate GitHub or verify access with:

```bash
git ls-remote https://github.com/poudelaman4/brand-motion-agent-skill.git
```

## Native loading by agent

### Claude Code skill

Claude Code discovers personal skills from `~/.claude/skills/` and project skills from `.claude/skills/`.

**Personal installation:**

```bash
set -euo pipefail
REPO_URL="https://github.com/poudelaman4/brand-motion-agent-skill.git"
SKILL_DIR="${HOME}/.claude/skills/animation-logo-skill"

mkdir -p "$(dirname "${SKILL_DIR}")"
if [ -d "${SKILL_DIR}/.git" ]; then
  git -C "${SKILL_DIR}" pull --ff-only
else
  git clone "${REPO_URL}" "${SKILL_DIR}"
fi
```

Restart Claude Code, then invoke it directly:

```text
/animation-logo-skill
```

Or ask naturally:

```text
Use the animation-logo-skill to audit this logo before proposing any motion.
```

**Project installation:**

```bash
REPO_URL="https://github.com/poudelaman4/brand-motion-agent-skill.git"
SKILL_DIR="$PWD/.claude/skills/animation-logo-skill"
mkdir -p "$(dirname "${SKILL_DIR}")"
git clone "${REPO_URL}" "${SKILL_DIR}"
```

Commit the project skill if the whole team should receive it.

### Open Code skill

Open Code discovers skills from `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`, and project equivalents. The universal installation above is sufficient:

```bash
SKILL_DIR="${HOME}/.agents/skills/animation-logo-skill"
test -f "${SKILL_DIR}/SKILL.md"
```

For a native Open Code location, use:

```bash
REPO_URL="https://github.com/poudelaman4/brand-motion-agent-skill.git"
SKILL_DIR="${HOME}/.config/opencode/skills/animation-logo-skill"
mkdir -p "$(dirname "${SKILL_DIR}")"
git clone "${REPO_URL}" "${SKILL_DIR}"
```

Restart Open Code and ask it to load the skill by name:

```text
Load the animation-logo-skill and create a plan for assets/my-logo.svg.
```

Open Code project-local discovery also supports `.agents/skills/animation-logo-skill/` and `.opencode/skills/animation-logo-skill/`.

### Cursor

Cursor versions differ in native Agent Skills discovery. For a reliable filesystem-native setup, install the skill in the project and add a Cursor rule that points to `SKILL.md`:

```bash
set -euo pipefail
REPO_URL="https://github.com/poudelaman4/brand-motion-agent-skill.git"
SKILL_DIR="$PWD/.agents/skills/animation-logo-skill"
RULE_DIR="$PWD/.cursor/rules"

mkdir -p "$(dirname "${SKILL_DIR}")" "${RULE_DIR}"
if [ -d "${SKILL_DIR}/.git" ]; then
  git -C "${SKILL_DIR}" pull --ff-only
else
  git clone "${REPO_URL}" "${SKILL_DIR}"
fi

cat > "${RULE_DIR}/brand-motion-agent-skill.mdc" <<'EOF'
---
description: Load the Brand Motion Agent Skill for logo motion planning, implementation, and QA.
alwaysApply: false
---

Read `.agents/skills/animation-logo-skill/SKILL.md` before handling a logo animation, brand mark, wordmark, emblem, logo reveal, logo loop, or logo-motion QA request. Follow its source-capability gate and task modes.
EOF
```

Open the project root in Cursor and start a new chat so the rule is discovered.

### Any filesystem-enabled agent

The skill is portable. Clone it anywhere and give the agent the absolute path to `SKILL.md`:

```bash
git clone https://github.com/poudelaman4/brand-motion-agent-skill.git \
  /absolute/path/to/animation-logo-skill
```

```text
Read /absolute/path/to/animation-logo-skill/SKILL.md and follow it for this logo-animation task.
```

## Quickstart: four task modes

### 1. Audit mode — inspect before designing

Use Audit when the source may be flattened, the brand geometry is unknown, or you need a risk report before rendering.

```text
Audit /absolute/path/to/assets/my-logo.png. Determine whether it is vector, layered raster,
flattened raster, or live text. Check alpha, resolution, connected components, possible occlusions,
and whether independent letters or leaves are safe. Do not render yet.
```

Optional diagnostic command:

```bash
SKILL_DIR="${HOME}/.agents/skills/animation-logo-skill"
python3 "${SKILL_DIR}/scripts/inspect_logo_assets.py" \
  /absolute/path/to/assets/my-logo.png \
  --minimum-area 500 \
  --max-components 30
```

The inspector is diagnostic only. Connected components are not guaranteed semantic logo layers.

### 2. Plan/storyboard mode — write the motion brief

Use Plan when you want a concept, frame contract, pivots, layer inventory, outputs, and QA gates before implementation.

```text
Plan a premium 2.4-second logo reveal for /absolute/path/to/assets/my-logo.svg.
Classify the mark, choose one primary motion pattern, record semantic pivots and z-order,
create a motion brief and manifest, specify a final hold and reduced-motion state,
and list the exact source layers and approvals needed before rendering.
```

Start from the templates:

```bash
SKILL_DIR="${HOME}/.agents/skills/animation-logo-skill"
cp "${SKILL_DIR}/assets/motion-brief-template.json" ./motion-brief.json
cp "${SKILL_DIR}/assets/motion-manifest-template.json" ./motion-manifest.json
```

### 3. Produce mode — implement and render

Use Produce after the source, task mode, timing, background, aspect ratio, and output contract are clear.

```text
Produce the approved logo animation from ./motion-manifest.json.
Use the approved source geometry, frame-driven timing, separate background compositions,
and exact checkpoint rendering. Deliver the master, requested variants, poster frame,
motion manifest, render commands, and QA report.
```

Remotion handoff example:

```bash
npx remotion render MyLogoComposition ./renders/my-logo.mp4 \
  --concurrency=2 --codec=h264 --crf=18
```

The renderer is intentionally not assumed by the skill. If Remotion, After Effects, or another renderer is unavailable, complete the renderer-neutral brief/manifest and report rendering as blocked.

### 4. Interactive mode — define states, not a one-shot timeline

Use Interactive for hover, press, active, selected, success, or reactive logo states.

```text
Use interactive mode for this logo. Define idle, hover, pressed, active, selected, and reduced-motion
states with 90–180 ms transitions, keyboard/focus parity, no motion-only state indicators,
and a static fallback for unsupported runtimes. Use dotLottie or SVG state-machine output if supported.
```

## Bundled utilities

| Utility | Purpose | Typical command |
|---|---|---|
| `inspect_logo_assets.py` | Inspect alpha, dimensions, bounds, and diagnostic components | `python scripts/inspect_logo_assets.py logo.png` |
| `validate_motion_spec.py` | Validate frame timing, bounds, easing, pivots, and final transforms | `python scripts/validate_motion_spec.py motion-manifest.json --check-files` |
| `make_checkpoint_contact_sheet.py` | Extract exact frame checkpoints into a review sheet | `python scripts/make_checkpoint_contact_sheet.py --input render.mp4 --output sheet.jpg --frames 0,30,60,96,119` |
| `compare_final_frame.py` | Compare a decoded poster frame with an approved reference | `python scripts/compare_final_frame.py --reference logo.png --encoded render.mp4 --frame 119 --tolerance 0.03` |
| `check_skill.py` | Dependency-free self-check of this package (frontmatter, reference links, schema, eval fixtures, validator smoke test) | `python scripts/check_skill.py` |

All Python utilities support `--help`. Optional dependencies are listed in `requirements.txt`.
`check_skill.py` needs only the standard library, so it works as a CI or pre-commit gate.
Run it after any edit to the skill to confirm the package is still internally consistent.

### Exact-frame QA example

```bash
SKILL_DIR="${HOME}/.agents/skills/animation-logo-skill"

python3 "${SKILL_DIR}/scripts/make_checkpoint_contact_sheet.py" \
  --input ./renders/logo.mp4 \
  --output ./qa/logo-checkpoints.jpg \
  --frames 0,24,48,72,95,96,119 \
  --columns 4

python3 "${SKILL_DIR}/scripts/compare_final_frame.py" \
  --reference ./assets/approved-logo.png \
  --encoded ./renders/logo.mp4 \
  --frame 119 \
  --tolerance 0.03 \
  --allow-opaque
```

Use `--allow-opaque` only when an opaque white or brand-background render is intentionally being compared to a transparent reference. Use `--require-alpha` when the deliverable must contain a real alpha channel.

For an opacity crossfade between an extracted raster layer and vector or whole-mark geometry, render direct stills at the start, midpoint, and end, then decode the same frames from the encoded file. A clean final frame and a clean contact sheet do not prove that the transition is clean.

```bash
npx remotion still MyLogoComposition ./qa/frame-24.png --frame=24
ffmpeg -y -v error -i ./renders/my-logo.mp4 \
  -vf "select=eq(n\\,24)" -vsync 0 -frames:v 1 ./qa/decoded-frame-24.png
```

## Source-capability and brand-safety rules

The skill's central guardrail is source honesty:

| Source type | Safe default | Independent motion |
|---|---|---|
| Vector/layered | Named groups, masks, trim paths, compatible morphs | Allowed when geometry is exposed |
| Layered raster | Approved semantic groups with tight crops and pivots | Allowed after layer approval |
| Flattened raster | Whole-mark, grouped, or mask reveal | Blocked unless reconstruction is approved |
| Live text | Outline or embed approved glyphs | Blocked until font/text source is approved |

Never treat OCR, segmentation, connected components, or automatic vectorization as canonical brand truth. A reconstruction is a new asset and needs a new approval gate.

## Motion manifest contract

A manifest records:

- source reference, checksum/profile, canvas, fps, and duration
- primary concept and task mode
- layer IDs, roles, source files, normalized bounds, pivots, and z-order
- half-open frame intervals, transforms, easing, confidence, and final-state status
- settle frame, hold start, poster frame, background variants, outputs, and target runtime
- reduced-motion behavior and acceptance checks

The canonical schema is `schemas/motion-spec.schema.json`. Validate before rendering:

```bash
python3 scripts/validate_motion_spec.py ./motion-manifest.json --check-files
```

A four-second 30 fps composition has 120 frames indexed `0–119`. A layer interval is half-open: `[start_frame, start_frame + duration_frames)`. Final-state layers must settle before the hold begins.

## Renderer and MLT/Kdenlive handoff

The skill is renderer-neutral. It can hand off to:

- **Remotion:** deterministic frame functions, React layers, local `staticFile()` assets, and H.264/MP4 output.
- **SVG/Lottie/dotLottie:** named vector groups, trim paths, themes, and interactive state machines.
- **After Effects:** shape layers, mattes, masks, and explicit keyframes.
- **MLT video automation framework:** transparent PNG sequences, ProRes 4444/XQ, or an approved lossless master for timeline assembly in Kdenlive/MLT.
- **FFmpeg:** frame extraction, stream inspection, alpha/codec checks, and contact-sheet generation.

Keep one canonical motion specification and timing model, but create separate square, vertical, horizontal, alpha, white, dark, and interactive compositions where the canvas or runtime requires it.

## Research and update loop

`references/sources.md` records research provenance for Agent Skills, motion design, accessibility, SVG/Lottie, Remotion, codecs, and brand precedents. The package does not silently fetch or apply web trends at runtime.

To update the skill safely:

1. Add or review a source in `references/sources.md`.
2. Separate normative technical documentation from tutorials and brand precedents.
3. Update `assets/motion-tokens.json` only when the change is broadly useful.
4. Update the relevant pattern/context reference.
5. Add or revise an evaluation in `evals/`.
6. Run manifest/script validation and compare with-skill versus baseline behavior.

## Evaluation status

The development evaluation set (`evals/evals.json`) has **5 cases with 24 assertions**
covering:

- flattened raster with unsafe independent-motion requests
- flattened raster transition ghosts and direct-frame QA
- layered vector education/LMS planning
- invalid manifest repair
- alpha, reduced-motion, aspect-ratio, and final-state requirements

`evals/trigger-queries.json` holds **12 positive and 8 negative** routing cases to
check that the skill fires on logo-motion work and stays out of unrelated tasks.

A self-check is runnable any time:

```bash
python scripts/check_skill.py
```

**Recorded results** (re-run after major edits and update this block):

| Check | Command | Result |
|---|---|---|
| Package self-check | `python scripts/check_skill.py` | **PASS** — 31 referenced paths, 5 evals / 24 assertions, validator smoke test |
| Valid manifest | `python scripts/validate_motion_spec.py evals/files/valid-motion-spec.json` | **PASS** |
| Invalid manifest | `python scripts/validate_motion_spec.py evals/files/invalid-motion-spec.json` | **FAIL (expected)** — all 8 planted errors caught |
| Flattened-source inspection | `python scripts/inspect_logo_assets.py evals/files/flattened-logo.png` | Reports alpha bounds + components and warns they are not semantic layers |

The local iteration also graded **10/10 assertions with the skill** versus **5/10
without the skill**. Treat every number here as a development benchmark, not a
substitute for human review of visual taste and brand fit.

## Troubleshooting

### The skill does not appear

- Confirm the directory is named `animation-logo-skill`.
- Confirm `SKILL.md` is directly inside that directory.
- Restart the agent after the first installation.
- For Claude Code, check `~/.claude/skills/animation-logo-skill/` or the project `.claude/skills/` path.
- For Open Code, check `~/.config/opencode/skills/`, `~/.agents/skills/`, or the project equivalents.
- For Cursor, confirm the `.cursor/rules/*.mdc` rule and open the project root.

### The clone returns 404

Verify that the repository is public, the URL is correct, and GitHub authentication is available:

```bash
git ls-remote https://github.com/poudelaman4/brand-motion-agent-skill.git
```

### Python utilities fail

```bash
cd "${HOME}/.agents/skills/animation-logo-skill"
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/inspect_logo_assets.py --help
```

### FFmpeg checks fail

Install FFmpeg and verify both binaries:

```bash
ffmpeg -version
ffprobe -version
```

### A flattened logo cannot animate independently

That is an expected `BLOCKED` result, not a reason to fabricate layers. Request vector/layered source, approve a reconstruction, or use the whole-mark/group fallback.

## License and attribution

Copyright © 2026 **Aman Paudel** ([GitHub: poudelaman4](https://github.com/poudelaman4)).

Released under the [MIT License](LICENSE).

Third-party logos, fonts, footage, codecs, and reference materials remain subject to their respective licenses and copyright. This repository does not grant permission to reuse third-party brand assets.

## Contributing

Contributions should preserve the package's core principles:

- approved geometry is immutable
- source limitations are explicit
- motion is deterministic and frame-driven where applicable
- one primary gesture beats a pile of effects
- final-state fidelity is measurable
- accessibility and reduced motion are part of production
- all new claims are labeled as observed, inferred, provisional, or blocked

Run the bundled validators and include an evaluation or visual QA artifact for behavior changes.
