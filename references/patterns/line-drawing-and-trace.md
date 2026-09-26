# Line Drawing and Stroke Draw-on Patterns

Line drawing requires a real stroked path; treat a synthesised stroke as `blocked` until approved. Classify against `feasibility.md` first.

## Contents

- Scenario blocks
- Dash mechanics
- Draw order and start points
- Limits
- Failure modes
- QA

## Scenario blocks

### LINE-01 — Continuous contour draw-on

**Intent:** craft, precision, heritage.

**Layers:** one `Z`-closed outline, `fill:none`, `stroke`, wordmark.

**Motion:** hold 100–200 ms, reveal as one stroke, settle.

**Timing:** 0.6–1.2 s; 400–800 ms hold.

**Easing:** `draw`; `round` cap for monoline marks.

**Anchors:** first vertex, chosen start, closing seam.

**Risks:** unclosed subpath, `miter` spike, short measured length.

### LINE-02 — Multi-stroke trace with junction order

**Intent:** a constructed system, not one gesture.

**Layers:** trunk, branches, junction nodes, wordmark.

**Motion:** draw the trunk first, so ink flows through each junction.

**Timing:** 0.9–1.8 s; 40–70 ms per branch.

**Easing:** `draw` per stroke, `linear` between; dwell at most 250 ms.

**Anchors:** junction centres, free endpoints, crossings.

**Risks:** T-junction notch, double-darkened caps, a stray connector.

### LINE-03 — Contour and edge trace

**Intent:** a lit rim on a solid mark.

**Layers:** filled silhouette, stroke-only duplicate, clip mask.

**Motion:** sweep a 5–10% dash window around the boundary.

**Timing:** 1.2–2.0 s per circuit.

**Easing:** `linear` crawl, `enter` for core fade.

**Anchors:** silhouette boundary, concave notch, occluder.

**Risks:** self-intersecting offset path, a rim under 1.0 px, residue in the hold.

### LINE-04 — Draw-then-fill

**Intent:** construction resolving into the canonical solid.

**Layers:** stroke copy, fill copy, counter masks, wordmark.

**Motion:** crossfade stroke-opacity to 0 as fill-opacity rises.

**Timing:** 700–1000 ms draw plus a 150–250 ms crossfade.

**Easing:** `draw` into `settle`; crossfade near-linear.

**Anchors:** silhouette boundary, counter, stroke-to-fill weight match.

**Risks:** stroke weight mismatched to the fill perimeter.

### LINE-05 — Travelling dash and comet

**Intent:** in-progress or routed, not built.

**Layers:** one path, short dash window, trail copy.

**Motion:** slide the window with `stroke-dashoffset`.

**Timing:** 1.0–2.0 s per circuit, linear.

**Easing:** `linear` only; easing stutters at the loop.

**Anchors:** dash head, path start, loop seam.

**Risks:** a dash longer than the path, a stuck offset.

### LINE-06 — Per-letter write-on

**Intent:** writing rhythm, no handwriting filter.

**Layers:** one stroked path per glyph or group.

**Motion:** reveal in reading order, 60–120 ms stagger, about 150 ms per glyph.

**Timing:** 0.9–1.8 s for up to about eight letters.

**Easing:** `draw` on glyphs, `enter` on the descriptor; never bounce each.

**Anchors:** baseline, glyph start vertex, word space.

**Risks:** text measured before the font loads, wrong stroke weight.

## Dash mechanics

```text
path length   L = getTotalLength() in user units
dasharray     L              single value ≡ "L L", period 2L
dashoffset    L * (1 - t)    t=0 hidden, t=1 drawn
floor         L >= measured path length, always
```

- Never author dashes in `%`: percentages resolve against the normalized viewport diagonal, not path length. Use absolute units or `pathLength="1"`, never mixed with real lengths.
- Hold `stroke-linecap` discrete; it cannot be tweened. `round` and `square` overshoot the end by half a stroke width.
- Close every continuous subpath with `Z`; an unclosed one is capped, not joined.
- Keep the rendered stroke at about 1.0 px or more (provisional); below that, 1x antialiasing breaks it into dots. Add `vector-effect: non-scaling-stroke` only to preserve device width under a scale.
- Drive Remotion from `useCurrentFrame()` and `interpolate`, `extrapolateRight: 'clamp'`; never `spring()`, whose 16% overshoot re-draws and snaps back.
- Use a trim modifier in Lottie: `ty: "tm"`, `m: 1` parallel, `m: 2` sequential, `o` a wrapped percentage, so `o: 0 → 360` travels.

**Limits:** Firefox miscalculates `getTotalLength()` on some paths; Safari has historically ignored `pathLength` for dash math (inferred). Trust measured lengths.

## Draw order and start points

1. List every path endpoint as a vertex and connect coincident ones; degree-1 vertices are free ends, degree-3-or-more are junctions.
2. Count odd-degree vertices: zero or two draws the mark without lifting the pen — a circuit starting anywhere, or a path starting at an odd vertex. More than two forces pen lifts.
3. Order strokes trunk-first; each branch meets an already-drawn node.
4. Set `T_i = L_i / v` per path, or author a designed sequence where semantics demand one.

Apply start priority: free endpoints, 12 o'clock clockwise for closed marks, then reading direction, baseline-left for LTR, mirrored for RTL.

- Do not start at a junction; two caps coincide at t=0 and double-darken.
- Split a symmetric closed mark at its apex, not on its axis of symmetry.
- Do not share one duration across paths; short strokes then snap.

**Forbidden shortcuts:** a `butt` branch meeting a trunk leaves a notch. Use `square`, or a filled circle of radius `stroke-width / 2` with a 60–100 ms pop.

## Limits

- A filled mark with no stroke variant; a synthetic stroke is a new asset.
- Non-monoline weight: `stroke-width` is a scalar, so author a taper as a filled outline.
- More than about six junctions (provisional); ordering stops reading as intent.
- Delivery below 64 px, where caps and hairlines stop being legible.
- Any synthetic stroke that changes the mark's perceived weight.

## Failure modes

- **Symptom:** a gap where an outline should close. **Repair:** add `Z`.
- **Symptom:** short paths snap, long ones crawl. **Repair:** set `T_i = L_i / v`.
- **Symptom:** a stroke crosses under at one junction, over at another. **Repair:** split and reorder.
- **Symptom:** the silhouette grows at the handoff. **Repair:** match the fill's perimeter weight.
- **Symptom:** a comet reads as a wobble. **Repair:** shorten the window to 5–10%.
- **Symptom:** a stroke double-darkens at t=0. **Repair:** start at a free end.

## QA

- Measure every path in Firefox and Safari; confirm 100% reveal.
- Confirm every subpath carries `Z`; inspect seams and crossings at 200%.
- Compare the final composite to the master at 32, 64, and 128 px.
- Render at 1x and 2x; confirm no stroke breaks into dots mid-draw.
- Check the final hold for residual offset, cap artifacts, or half-drawn paths.

These are planning ranges and observed behaviours, not a reason to force draw-on onto a solid mark.
