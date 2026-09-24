# Motion Foundations

## Contents

- Layer hierarchy
- Pivots and bounds
- Timing grammar
- Easing tokens
- Stagger and overlap
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
