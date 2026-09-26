# Advanced Mechanics

Renderer mechanics for draw-on, separation, morph, and sweeps. Read `motion-foundations.md` for the craft layer, then the sibling file.

## Contents

- Time bases
- Determinism
- Path measurement
- Cross-browser hazards
- Stroke mechanics per target
- Separation mechanics per target
- Morph mechanics
- Gradient and light sweeps
- Render and alpha notes

## Time bases

| Target | Clock | Value lands in |
|---|---|---|
| SVG and CSS | `@keyframes` percentages over a 0.6–2.2 s duration | dash offset, transform, opacity, `d`, clip path, stop offset |
| SVG Web Animations API | `el.animate()`, scrubbed via `anim.currentTime` in ms | same |
| Remotion | `useCurrentFrame()`, zero-based, last frame `durationInFrames - 1` | inline style, SVG attributes |
| Lottie | keyframe `t` in frames, `fr` as fps, `ip`/`op` bounds | `k` |
| After Effects | `time` in seconds, or `time * fps` | keyframes, expressions |

Convert with `fraction = frame / (durationInFrames - 1)`, `seconds = frame / fps`, `degrees = (frame / durationInFrames) * 360` — denominators differ.

## Determinism

Require every animated value to be a pure function of the frame number.

**Forbidden shortcuts:** runtime randomness, wall-clock time, performance timing, timers and rAF, CSS animations and transitions inside a Remotion composition, and module-scope mutable state. Substitute a seeded generator keyed on a stable string: Remotion's `random('logo-seed')`, and `seedRandom(offset, timeless)` in After Effects. Treat `time` and functions of `time` as deterministic there, and `wiggle()` as not reproducible across layer re-creation. Treat Lottie as deterministic because it is keyframes, and expressions in a `.lottie` container as a portability risk.

## Path measurement

Treat `getTotalLength()` and `getPointAtLength()` as real, Baseline-supported APIs; a headless DOM cannot measure. Measure once in a real browser and bake it into a manifest or generated module.

Normalize by authoring `pathLength` on the source, or by baking measured lengths as CSS custom properties. Never mix `pathLength` with real measured values on one element.

```text
mark      L 812.44  subpaths 2  closed false
wordmark  L 431.02  subpaths 9  closed false
```

Record `subpaths` so compound paths stay split.

## Cross-browser hazards

| Hazard | Symptom | Repair |
|---|---|---|
| `stroke-dasharray` in `%` | Resolves against the viewBox diagonal | Use user units, or `pathLength` |
| Safari decimals | A sliver of stroke at one end | Round up: `Math.ceil(L) + 1` |
| Firefox lengths on some paths (`observed`) | `getTotalLength()` wrong; the draw never completes | Verify in-engine; use pure-JS math |
| Safari `pathLength` in dash math (`observed`) | Wrong animation speed | Ship measured lengths as truth; re-check per engine version |
| Library pixel rounding | `117px` offset against a `116.619` dash array | Disable rounding, or normalize to `1` and `0` |
| Compound path `M…Z M…Z` | Sums all subpaths; the pattern never resets, so it draws as one run | Split per subpath first |
| viewBox scaling or zoom | Hairlines thin; zoom desyncs the pattern | `vector-effect: non-scaling-stroke` |

## Stroke mechanics per target

Apply `dasharray = L` and `dashoffset = L * (1 - t)`, `t` from 0 to 1. One value of `L` equals `L L`, period `2L`: offset `L` hides, `0` draws.

| Target | Mechanism | Constraint |
|---|---|---|
| SVG and CSS | `stroke-dasharray: L`, animated offset; `pathLength="1"` gives `1` and `0` | `dasharray` at least `L` or the path re-dashes mid-draw; `stroke-linecap` is discrete and untweenable |
| Remotion | `interpolate(frame, ...)`; set `strokeDasharray` unconditionally | `extrapolateRight: 'clamp'` is mandatory; the default extends and re-draws. Never `spring()`, which overshoots. Clear `delayRender` within the timeout |
| Lottie | Trim paths `ty: "tm"`, `s`/`e` at 0–100% of the shape's length | `m: 1` trims each subpath, `m: 2` concatenates. A trim below its path does nothing. `[UNVERIFIED]` cap and join integers |
| After Effects | Trim Paths Start, End, and Offset on shape layers | Shape-layer paths only. Keep durations whole frames; delete the last keyframe when looping with time remap or each cycle repeats a frame |

**Forbidden shortcuts:** never emit a Lottie group transform that is not last in its `it` array, or a stroke after it.

## Separation mechanics per target

| Target | Required setup | Hazard |
|---|---|---|
| SVG and CSS | `transform-box: fill-box` with `transform-origin: center` | The default origin is the canvas origin, so parts drift inward. Reorder the DOM per frame, or clip a background-colored copy of the front parts; `z-index` does nothing |
| Remotion | Sort by depth per frame, keyed on a stable id | Index-keyed sorting thrashes reconciliation per frame |
| Lottie | Parent with `parent`, nest groups, fake depth with scale, opacity, tint | No blur primitive in the shape spec; layer effects vary by player |
| After Effects | 3D layers depth-sort automatically under a camera | 3D layers antialias differently; render at 1.5× and downscale |

Count blur as a per-frame rasterization cost; cap blurred parts near 12. Grouping properties — `opacity` below 1, `filter`, `clip-path`, `mask`, non-visible `overflow` — flatten the 3D context, so nest `translateZ` and `opacity` separately. On a flattened raster, build mask separation from N identical copies of one image clipped to bands or wedges; see `patterns/separation-and-explode.md`.

## Morph mechanics

Require matched segment counts and command types, index correspondence so point *i* names the same feature in both shapes, and primitives converted to paths first. Normalize both shapes to one signature, normally absolute commands and `M … C … C … Z` for a closed shape, or interpolation degrades to discrete steps.

Treat a morph as neither transform nor tint: it cannot use the manifest transform channel in `qa/motion-manifest.md` and needs its own plan record with shapes, vertex count, and correspondence. Check intermediate frames, not only endpoints, for self-intersection, where the outline crosses itself, and topology change, where a counter opens or closes.

## Gradient and light sweeps

Animate stop offsets and the sweep angle; confine a sweep to the mark with a mask, not a wider canvas. Register any custom property read inside a gradient with `@property`, or it jumps 0 to 360 discretely and the mask snaps. Drive Remotion values inline from `useCurrentFrame()`, never `@keyframes`. Use a track matte in Lottie and After Effects; it exports to Lottie more faithfully than a mask. Choose `multiply` for an ink press, `screen` or `plus-lighter` for light, `overlay` for a tonal push.

Check the 8-bit banding hazard: a low-contrast gradient over an alpha master quantizes into visible steps, so keep the highlight narrow, inspect on the delivery background, and keep the sweep off the mark. Run 400–800 ms, after the mark reads, per `contexts/premium-and-minimal.md`.

## Render and alpha notes

Composite gradients, blends, and blurs in premultiplied space and convert to straight alpha for delivery; mixing conventions darkens edges. `screen` and `plus-lighter` over transparent black are a no-op, so a light sweep needs an explicit backdrop.

Keep the alpha master separate from the white and brand-color fallbacks per `delivery/alpha-and-codecs.md`, and never bake a background into it. Treat a filter-based effect as non-portable until checked in the named target player, and keep player trim and matte mapping `provisional` until observed on the installed version.
