# Motion Foundations

## Contents

- Layer hierarchy
- Pivots and bounds
- Timing grammar
- Easing tokens
- Stagger and overlap
- Stroke and path mechanics
- Masks and wipes
- Final-state lock
- Acceptance criteria
- Performance
- Manifest fields

## Layer hierarchy

Use semantic roles instead of visual guesses:

1. Background or matte
2. Rear connectors and structural details
3. Back leaves, panels, or modules
4. Core symbol
5. Foreground details and center
6. Wordmark and descriptor
7. Optional finishing effect

Every role must state whether it is locked, animatable, optional, or campaign-only.

## Pivots and bounds

Store geometry in normalized source-artboard coordinates with a top-left origin. Bounds are `[x_min, y_min, x_max, y_max]`; pivots are `[x, y]`. A pivot may be outside a tight crop when a semantic anchor is outside the visible pixels.

- Leaf/petal: root, stem, or base junction
- Letter: baseline, cap-height center, or approved optical anchor
- Geometric module: grid anchor or connector
- Badge ring: center only when rotationally symmetric
- Wordmark: baseline or lockup anchor, not arbitrary box center

For cropped layers, record both crop bounds and pivot. If inferred, label the pivot `provisional` and show a pivot overlay before production.

## Timing grammar

Use a frame contract:

```text
duration_frames = fps × seconds
last frame = duration_frames - 1
layer interval = [start_frame, start_frame + duration_frames)
settle_frame = first frame guaranteed canonical
hold_start_frame = first frame guaranteed static
poster_frame = approved static frame, normally the last frame
```

A useful one-shot structure at 30 fps is:

```text
0–6       establish or mask opens
6–60      primary mark gesture
30–75     wordmark or secondary detail may overlap
75–96     settle and remove temporary scaffolding
96–119    hold canonical final state
```

Adapt to the logo's complexity. Do not force a four-second sequence onto a simple mark.

## Easing tokens

| Token | Cubic-bezier equivalent | Use |
|---|---|---|
| `settle` | `0.2, 0, 0, 1` | Repositioning, scale, modular assembly |
| `enter` | `0, 0, 0.2, 1` | Controlled deceleration into place |
| `draw` | `0.45, 0, 0.55, 1` | Stroke/path reveal |
| `organic` | `0.34, 1.15, 0.64, 1` | Gentle unfurl; limit overshoot |
| `snap` | `0.85, 0, 0.15, 1` | Grid-locked construction |
| `play` | one-pass spring | Explicitly playful accents only |
| `path-linear` | linear | Fixed route or orbit only |

Avoid generic bounce on every element. Identity-critical geometry should use zero overshoot and a clean stop. Keep token definitions synchronized with `assets/motion-tokens.json`.

## Stagger and overlap

- Start related groups close enough to read as one gesture.
- Use 40–80 ms stagger for meaningful groups; use smaller offsets for dense letters.
- Preserve reading order for left-to-right, right-to-left, vertical, and non-Latin scripts.
- Let the wordmark begin when the primary silhouette is readable, not necessarily when every leaf has stopped.
- Overlap at least two phases in a two-to-four-second reveal so the animation feels continuous rather than queued.
- Hold the final state long enough to recognize the identity.

## Transform hierarchy

Prefer, in order:

1. Opacity
2. Translation
3. Scale
4. Rotation
5. Mask/trim reveal
6. Morph only with compatible paths
7. Texture or generated atmosphere outside the canonical logo

Use a fixed camera and fixed artboard. Use transforms and opacity rather than changing layout dimensions each frame.

## Stroke and path mechanics

Measure every subpath before authoring any dash value, and keep the arithmetic in user units. Never inherit a dash, offset, or cap from a mark that merely looks similar.

```text
quantity     value                     note
L            getTotalLength()         user units, measured per subpath
dasharray    L                        a single value reads as "L L"
period       2L                       one dash plus one gap
hidden       dashoffset = L           t = 0, path fully hidden
drawn        dashoffset = 0           t = 1, path fully drawn
formula      dashoffset = L * (1 - t) t runs 0 to 1 across the reveal
floor        L >= measured length     dasharray never falls below the path
```

- Hold `dasharray` at or above the measured path length. A shorter array re-dashes the remainder partway along the path and shows a second line behind the first, which reads as a doubled contour once the reveal completes; this is the most common draw-on defect.
- Set `dashoffset` to `L` to hide the path and `0` to draw it. Because a single-value `dasharray` behaves as `L L`, the period is `2L` and the offset travels exactly one dash per `L`.
- Author `stroke-dashoffset` in absolute user units or against a normalized `pathLength`. A percentage resolves against the normalized viewport diagonal rather than the path, so the reveal ends early or late by a factor of the artboard aspect ratio.
- Do not mix a normalized `pathLength` with real measured lengths on one path.
- Hold `stroke-linecap` discrete. It cannot be tweened, and switching it mid-draw registers as a width change at the head rather than as a reveal.
- Account for the cap overshoot: `round` and `square` extend the stroke by half a `stroke-width` past the nominal end, so the first and last 1–3% of the dash is not the geometry it appears to be.
- Close every continuous outline with `Z`. An unclosed subpath is capped at the seam rather than joined, leaving a break where the contour should meet itself.
- Add `vector-effect: non-scaling-stroke` when a viewBox scale would thin a hairline; it preserves device width under scale and costs one extra paint pass.
- Keep the rendered stroke at 1.0 px or wider (`provisional`). Below that, 1x antialiasing breaks the line into dots and the mark reads as stippled rather than drawn.
- Normalize with `pathLength` when a measured length is awkward to hand-author: set `pathLength="1"` and drive `dasharray` and `dashoffset` from 0 to 1.
- Treat measured lengths as the shipping source of truth. Some players have ignored `pathLength` for dash math (`inferred`), so a normalized reveal can preview correctly and still ship wrong; re-measure in the target player before delivery.

Keep the numbers in user units until the composition scale is fixed. Read `patterns/line-drawing-and-trace.md` for start points, junction order, and per-path duration, and `implementation/vector-and-lottie.md` for trim-path and export behaviour.

## Masks and wipes

Name this family by its industry word: a wipe. Treat WORD-02 directional mask as a wipe, and treat a whole-mark wipe as the fallback reveal whenever every other reveal channel is gated, per `technique-selection.md`.

| Type | What it is | Main artifact | Typical reveal |
|---|---|---|---:|
| `alpha` | Opacity channel of a shape or image | Halo or soft edge where the source alpha is not clean | 0.6–1.4 s |
| `luma` | Brightness channel of a raster | Fringe on a dark mark; tonal shift across the reveal | 0.6–1.2 s |
| `vector` | Gradient painted into a mask element | Gradient banding at 8-bit output | 0.8–1.6 s |
| `clip` | Hard geometric boundary with no softness | Straight cut through a counter or a stroke end | 0.5–1.0 s |
| `conic` | Angular sweep from a single origin | Sweep direction that contradicts the mark's structure | 0.8–1.6 s |
| `band` | Straight moving edge across the mark | Banding in a wide gradient applied to a raster | 0.6–1.1 s |
| `wedge` | Sector cut from a centre point | Visible vertex parked at the origin | 0.6–1.0 s |

| Source | Needs |
|---|---|
| Shape layer | A named mask path in the authoring tool, with group names preserved through export |
| Track matte | A matte layer aligned to its target and the matted property set explicitly |
| Alpha extracted from a raster | Original-resolution pixels, a clean matte, and pruned residual low-alpha components |
| `clipPath` | A geometry-only element in user units; a clip carries no feather |
| After Effects matte | A named matte layer, an explicit matte assignment, and a preflight confirming the matte survives export |

- Treat a mask that clips a counter mid-transition as a typography failure, not a rendering artifact: a half-formed letter reads as a font error. Choose the reveal direction from the mark's structure — growth direction, stroke direction, or the light side of the composition — rather than from whichever axis is convenient, and record the decision. Counter clipping sits with the other typography failures in `qa/failure-catalog.md`.
- Report any feather, and report it as part of the identity decision rather than a renderer setting. Feathering widens the visible edge by its own radius on every side, so a 4–12 px feather softens a monoline mark past recognition at delivery sizes.
- Replace a mask with a transform when the reveal would clip the mark below its minimum legible size. A transform moves whole geometry and cannot bisect a counter; a mask can, and will.
- Do not hide a rejected reveal behind a feather or a gradient ramp. Report it as `blocked` and offer the whole-mark wipe instead.
- Keep mask geometry out of the canonical logo. A mask belongs to the reveal, and the poster frame must composite clean with no mask residue.

Read `patterns/wordmark-and-lockup.md` for the directional wipe on type, `patterns/separation-and-explode.md` for band, wedge, and conic masks over flat art, and `qa/qa-checklist.md` for the reveal checks.

## Final-state lock and acceptance

The final state is a golden state. Verify separately:

- canonical source geometry, path/shape positions, counters, kerning, clear space, and approved color
- alpha mask and composited RGB against the reference
- encoded output within a documented color/codec tolerance
- no construction guides, blur, glow, residual transparency, or clipping
- first and last states match for loops
- alternate aspect ratios have their own approved composition checks

Do not claim byte or pixel identity after lossy H.264/WebM encoding or resampling. Record source checksum, color profile, renderer, codec, pixel format, and tolerance.

## Performance

- Extract or request layers once; do not segment every rendered frame.
- Use tight crops instead of many full-canvas transparent images.
- Preload local assets through the renderer's normal image component.
- Benchmark render time and memory on the lowest supported device.
- Use concurrency appropriate to the machine; do not treat a desktop render as proof of mobile performance.
- Keep a static poster and reduced-motion output so motion is never the only way to identify the brand.

## Manifest fields

For each layer record:

```text
id, role, source, bounds, pivot, z_index, start_frame, duration_frames,
from, to, easing, confidence, locked, final_state
```

For the composition record:

```text
name, fps, duration_frames, canvas, source_reference, source_checksum,
source_profile, primary_concept, settle_frame, hold_start_frame,
poster_frame, reduced_motion, background_variants, outputs, target_player, renderer
```
