# Setup and Environment

Determine what this machine can do before promising a deliverable. Every task the skill can do has a floor of zero installed dependencies, and each step above that floor needs a named tool.

## Contents

- Probe first
- The renderer ladder
- What each mode needs
- Degrading instead of failing
- Viewer device
- The producer machine
- Limits

## Probe first

```bash
python scripts/check_environment.py            # human-readable report
python scripts/check_environment.py --json     # machine-readable
python scripts/check_environment.py --mode produce
python scripts/check_environment.py --self-test
```

The probe reports four states and never installs anything.

| State | Meaning | Action |
|---|---|---|
| `ok` | Available and usable now | Proceed |
| `degraded` | Available, but a documented feature is lost | Proceed, and state the loss in the brief |
| `missing` | Not installed | Offer the printed install command, or deliver below that floor |
| `blocked` | Not installable here | Use the documented alternative and say so |

Report a `missing` or `blocked` state to the user as a choice, not a fait accompli. The probe prints a per-platform install command; installing is the user's decision, because on a locked-down machine it may not be possible and because a heavy install changes their system.

## The renderer ladder

Choose the highest rung the environment actually supports. Each rung down costs fidelity or file size, and the choice belongs in the brief.

| Rung | Renderer | Needs | Produces | Reach |
|---:|---|---|---|---|
| 1 | SVG and CSS | Nothing beyond a browser | Vector, resolution-independent, interactive | Web, product UI, Lottie source |
| 2 | Lottie or dotLottie | A Lottie authoring tool, or hand-authored JSON | Vector, small, themeable, stateful | Web and app UI |
| 3 | Remotion | Node 18+, a Chrome binary, the Remotion CLI | Video from a frame-driven React composition | Every video deliverable |
| 4 | After Effects | A licensed install, plus a render pipeline | Video and broadcast masters | Broadcast, cinema, high-end delivery |
| 5 | A rendererless pipeline | Nothing | A brief and a validated manifest only | Audit and plan modes |

Two rules govern the choice. First, **never climb a rung the environment cannot support** — a video promised on a machine with no renderer is a broken commitment, so complete the manifest and mark rendering `blocked` instead. Second, **do not stay below a rung the deliverable needs**: a broadcast master cannot be a CSS animation, and an app icon set cannot be a video.

Remotion needs a Chrome or Chromium binary because it renders in headless Chrome. It normally downloads its own on first run; on an offline or locked-down machine that download fails and rendering becomes `blocked`. Probe before promising a render.

## What each mode needs

| Mode | Minimum | With the probe `ok` | With something `missing` |
|---|---|---|---|
| `audit` | Python 3.10+ | Full structural report | Report the gap and inspect the source by hand |
| `plan` | Python 3.10+ | Profile, rank, and gate techniques | Write the brief from the source and the brief template |
| `produce` | Python, Pillow, NumPy, FFmpeg, Node | Render, checkpoint, and verify | Manifest and brief only; rendering `blocked` |
| `interactive` | Node | State machines and runtime motion | Static states until a runtime exists |

Only Pillow, NumPy, and SciPy are genuinely optional, and only for raster work. **Vector profiling needs nothing beyond the standard library**, so an SVG profiles on a bare Python install. That is deliberate: the most common input should never be blocked by a missing dependency.

FFmpeg is the only hard external dependency for evidence. Without it there is no checkpoint contact sheet and no decoded-frame comparison, which means the QA step cannot be evidenced — say that rather than implying the checks passed.

## Degrading instead of failing

A missing dependency must never end the task. Each has a documented fallback, and the fallback belongs in the brief as a recorded decision.

| Missing | Fallback | Cost |
|---|---|---|
| SciPy | Component, hole, and stroke-width metrics report `null`; confidence drops | Raster technique ranking gets weaker; request a vector source |
| FFmpeg | Deliver the manifest and the source; mark QA evidence `blocked` | No frame-accurate evidence |
| Pillow and NumPy | Profile the vector only; treat a raster source as unprofiled | No technique ranking for raster input |
| Node | Write the manifest and hand off; mark rendering `blocked` | No video from this machine |
| A Chrome binary | Remotion may fetch one; if it cannot, use the Lottie or SVG rung | Smaller deliverable set |
| potrace | Ask for an approved vector source rather than tracing | Traced contours are not authored geometry |

Never substitute a lower-fidelity technique silently. A mask wipe delivered in place of a stroke draw-on must be recorded as a substitution with its reason, because the two produce visibly different results and the user may have approved the first.

## Viewer device

The producer machine and the viewer device are different problems. The probe covers the producer. For the viewer, state assumptions rather than measuring them, because the agent has no access to the user's screen.

- **Device pixel ratio.** Author vector at 1× and confirm at 2× and 3×, or a hairline stroke lands on a half pixel and disappears. A stroke below about 1 device pixel is the single most common small-size defect.
- **Decode capability.** Assume the least capable target in the delivery matrix, not the developer's machine. Prefer a container the target actually decodes; MP4 alpha is not reliably decoded in browsers, so a transparent web asset needs WebM VP8 or VP9.
- **Reduced motion.** Treat `prefers-reduced-motion` as a first-class audience, not a preference. Deliver the reduced variant as an asset rather than relying on a runtime override alone.
- **Performance.** A mark in a persistent header renders for the life of the page. Keep the animated area small and prefer transform and opacity, then measure rather than assume.
- **Screen size.** Test at the smallest real render, which for a notification or a favicon is far smaller than any preview.

Report which of these could not be verified rather than implying the asset is universally safe.

## The producer machine

What the probe reports and what it deliberately does not.

| Reported | Not reported |
|---|---|
| Python version and platform | GPU model or driver |
| Installed package versions | Available RAM and free memory while rendering |
| FFmpeg, FFprobe, Node on PATH | Whether the network can reach a package registry |
| Disk free against a floor per output class | Whether a headless browser will actually launch |
| Logical core count | Thermal throttling on a laptop |

The probe does not try to infer the viewer machine's capability, and it does not claim a render will be fast. On one or two cores, a Remotion render is slow enough that the user should be told before it starts rather than after.

Two floors worth stating explicitly: about 10 GB free covers standard-definition and 1080p output with intermediates, and about 40 GB is the working figure for 4K. A render that fills the volume fails part-way and leaves an undeliverable state on disk.

## Limits

- The probe reports what exists, not what will succeed. A tool on PATH can still fail on a given input, and a first Remotion run can still fail on a network fetch.
- Never install anything without the user's agreement. Print the command and let them run it.
- Never report `ok` for a capability that was not probed. Omit it instead.
- Treat a missing renderer as a delivery-scope change, not a technical inconvenience, and get agreement before falling to a lower rung.
- Re-probe after an install. A capability that was `missing` in the brief and is `ok` in the render is a provenance gap worth recording.
