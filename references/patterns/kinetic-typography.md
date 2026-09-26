# Kinetic Typography Patterns

Apply per-glyph, per-axis, or path-driven motion to approved letterforms only, and hold the canonical wordmark unchanged at the end.

## Contents

- Source requirement
- Reveal mode selection
- Scenario blocks
- Per-glyph timing model
- Measurement APIs
- Accessibility
- Limits
- Failure modes
- QA

## Source requirement

Gate every scenario here on one of two sources. Accept nothing else.

- **Outlined glyph paths:** one `<path>` per glyph, with original advance widths and master kerning recorded alongside.
- **Live text with a guaranteed-loaded font:** a bundled or outlined face resolved before frame 1.

Declare live text `BLOCKED` for any pipeline that cannot guarantee the face at render time. Outline or embed it; never depend on a remote one.

Keep the final state byte-identical to the approved wordmark. Tracking, sidebearings, kerning, counters, and baseline are identity, not decoration. **Forbidden shortcuts:** re-typesetting at a different weight, re-typing into a substitute family, normalizing tracking afterwards.

## Reveal mode selection

| Mode | Requires | Reads as | Main risk |
|---|---|---|---|
| Fade | Any approved source | Neutral | Static; no kinetic identity |
| Mask reveal | Line or word split | Editorial | Descender clipping, arbitrary wipe |
| Tracking settle | Spacing delta, one run | Refined | Reads as font substitution |
| Per-glyph rise | Glyph paths or measured text | Energetic | Loading-screen feel past 12 glyphs |
| Axis animation | Variable font, live text | Modern | Widths change; re-verify lockup |

Default to fade or mask, and prefer the quieter `patterns/wordmark-and-lockup.md` modes when a reveal has no structural reason to exist. Take per-glyph rise only at 12 glyphs or fewer, and axis animation only with a shipped variable font.

## Scenario blocks

### KINE-01 Per-glyph stagger

**Intent:** distribute one word's appearance across 400–700 ms in reading order.

**Layers:** a group per glyph, or one `<text>` split into positioned `<tspan>`s.

**Motion:** rise each glyph 0.2–0.35 em off the baseline and fade in. Do not rotate.

**Timing:** 0.6–1.1 s; 40–70 ms per glyph; stagger at most 400 ms.

**Easing:** `enter`, zero overshoot throughout.

**Anchors:** the baseline or lockup anchor, never a box center.

**Risks:** per-glyph bounce, kerning lost to the split, ligatures broken, reversed order on right-to-left runs.

### KINE-02 Baseline mask reveal

**Intent:** reveal a word from behind the baseline as one gesture, tracking intact.

**Layers:** one mask rectangle per line or word over the unmodified text run.

**Motion:** animate a covering rectangle or `clip-path: inset()` closed to open; reserve padding below the baseline for descenders.

**Timing:** 0.6–1.1 s; hold 500–800 ms.

**Easing:** `settle` on the mask edge.

**Anchors:** the leading edge, left to right, mirrored for right-to-left.

**Risks:** a meaningless wipe direction, shaved descenders, stale pre-font metrics.

### KINE-03 Variable-axis weight morph

**Intent:** carry emphasis or state change on weight or width, not position.

**Layers:** the live text run, one animated axis.

**Motion:** animate `font-variation-settings` to the approved axis values, listing every animated axis in every keyframe.

**Timing:** 0.8–1.4 s.

**Easing:** `settle`; zero overshoot on the canonical state.

**Anchors:** the run's own baseline; each axis changes advance widths.

**Risks:** axes not reverting at the hold, and a layout shift the container does not reserve.

**Forbidden shortcuts:** encoding an axis in the manifest `transform` channel. An axis is not a transform; plan the channel in the brief.

### KINE-04 Text on a path

**Intent:** bind a word to a badge ring or seal; keep it out of modern-minimal wordmarks.

**Layers:** a hidden guide `<path>` carrying `pathLength`, plus one `<textPath>`.

**Motion:** animate `startOffset` from 0% to 100% to crawl, or hold the offset and animate the draw.

**Timing:** 1.2–2.0 s.

**Easing:** `path-linear` for the crawl, `draw` for a traced arc.

**Anchors:** the guide path, not the text box.

**Risks:** borrowed tradition, baseline drift on tight arcs, per-engine `pathLength` differences.

### KINE-05 Initial to lockup

**Intent:** hand off from an initial to the full wordmark in one continuous gesture.

**Layers:** the approved initial, the descriptor, and the wordmark at canonical spacing.

**Motion:** hold the initial, then resolve the wordmark from the same baseline; prefer a mask or tracking settle to per-glyph motion.

**Timing:** 1.0–1.8 s; wordmark 500–1400 ms; hold.

**Easing:** `settle`, then `enter` for opacity.

**Anchors:** the shared baseline plus the initial's optical anchor.

**Risks:** the wordmark competing with the mark, two baselines, an outranking descriptor.

## Per-glyph timing model

Record one entry per glyph so the model regenerates in any runtime.

```text
glyph_index      integer, 0-based, reading order
source           path id or source character
advance_width    user units, from the master metrics
start_fraction   0.0–1.0, cumulative advance / computed text length
delay_ms         glyph_index * stagger_ms
duration_ms      shared, normally 400–700 ms
```

Drive `start_fraction` from cumulative advance, not index, so wide glyphs do not lag. Fit the stagger inside 40–70 ms per glyph and never exceed roughly 400 ms total; past that it reads as a loading screen. Do not let a per-glyph reveal bounce independently: share one easing curve and keep zero overshoot on identity-critical type.

## Measurement APIs

| API | Returns | Limit |
|---|---|---|
| `getNumberOfChars` | Glyph count | Characters, not ligature clusters |
| `getComputedTextLength` | Total advance | Depends on the resolved face |
| `getSubStringLength` | Advance of a range | Ignores `x`-attribute spacing |
| `getStartPositionOfChar` | Glyph origin | Advance midpoint, not ink |
| `getEndPositionOfChar` | Glyph terminal | Excludes trailing sidebearing |
| `getRotationOfChar` | Degrees | Zero unless on a path |
| `getExtentOfChar` | Ink bounding box | Excludes strokes and masks |
| `getTextLength` / `textLength` | Forced run length | Distorts without `lengthAdjust` |
| `lengthAdjust` | `spacing` or `spacingAndGlyphs` | The latter rescales counters |
| `<textPath startOffset>` | Distance along guide | Percentages need `pathLength` |
| `<textPath method>` | `align` or `stretch` | `stretch` alters letterforms |

Measure only after `document.fonts.ready`; a late face invalidates every number, and `getSubStringLength` stays blind to `x` spacing, so per-letter masks built from it drift on a justified wordmark.

Sample guide-path geometry with `getTotalLength` and `getPointAtLength`, which SVG 2 moved up to `SVGGeometryElement`; `getPathSegAtLength` and the `createSVGPathSeg*` methods were removed. These APIs are absent from a headless DOM, so measure once in a real browser, bake the numbers in, and mark the result `observed`.

## Accessibility

Supply a static equivalent for every sequence, because the reveal carries meaning over time. Present the approved final state immediately under reduced motion, with no stagger. Keep the reveal in reading order, and never let motion hide a character long enough to change how the name is read. Do not make kinetic type the only carrier of hierarchy.

## Limits

- More than about 12 glyphs at small sizes.
- Scripts without per-glyph advances.
- Live text with a web font that may fail to load.
- Any split separating a ligature or kerning pair.
- Vertical or right-to-left scripts, where per-letter timing breaks reading order.
- Justified or tracked-out wordmarks, where `x` spacing invalidates substring metrics.

## Failure modes

**Symptom:** glyphs appear out of order. **Repair:** mirror the index on right-to-left and vertical runs, or drop to a whole-line mask.

**Symptom:** letters overlap and the lockup collapses. **Repair:** a face resolved after measurement; re-measure after `document.fonts.ready` and rebake advances.

**Symptom:** the settled lockup is wider than the master. **Repair:** an axis run that never returned to the approved `wght` and `wdth`; restore both.

**Symptom:** kerning reads wrong after the split. **Repair:** per-letter `<tspan>`s killed the pair; disable kerning and make the unkerned layout canonical, or revert to a per-line mask.

**Symptom:** descenders are shaved. **Repair:** raise the mask box or add `padding-bottom` instead of widening the clip.

**Symptom:** the sequence reads as a loading screen. **Repair:** the stagger passed roughly 400 ms; cut the delay and use a whole-word mask.

## QA

- Compare the settled frame to the master glyph by glyph, not as one silhouette.
- Measure at both `wght` and `wdth` extremes; confirm kerning and sidebearings match.
- Inspect descenders, diacritics, and any ligature the split could have broken.
- Confirm the reduced-motion build shows the final state with no residual transform.
- Verify reading order, direction, and per-letter mask edges at delivery size.

Timing values here are `inferred` from cross-renderer behaviour and stay `provisional` until measured against the approved master.
