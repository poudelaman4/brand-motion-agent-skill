# Separation, Explode, and Deconstruction Patterns

Separate independently addressable parts of an approved mark, then reassemble; treat this as a capability check, not a decorative effect.

## Contents

- Source requirement
- Scenario blocks
- Depth without 3D
- Ordering rules
- Frame contract
- Limits
- Failure modes
- QA

## Source requirement

Require capability level R3 — independent siblings with known bounding boxes, per `taxonomy.md`. Record `id`, `role`, bounds, centroid, and z-order per part.

Treat a single-path source as `BLOCKED`. Approved fallbacks, in order:

1. Manually approved grouped bands
2. A whole-mark radial mask
3. An explicit manual part list

Do not promote a connected-component count to a layer inventory; components split on antialiasing and touching pixels. Reconstruction needs approval, per `feasibility.md`.

## Scenario blocks

### SEP-01 — Radial burst separation

**Intent:** express energy and release.

**Layers:** four to twelve parts, no ring.

**Motion:** throw each part along its own radius, 0.25 × widest part.

**Timing:** 0.6–1.0 s out, 0.5–0.8 s back, 30–50 ms stagger.

**Easing:** `settle`, 0.15 × θ follow-through.

**Anchors:** shared centroid.

**Risks:** a part holding the centroid never moves.

### SEP-02 — Axis separation and reassembly

**Intent:** engineering or rebuild narrative.

**Layers:** R3 siblings in one baked space.

**Motion:** translate along `normalize(center − partCentroid)`, 0.18 × logo width or 1.2 × part width.

**Timing:** 0.7–1.1 s out, 0.5–0.8 s back, 40 ms stagger.

**Easing:** `settle`, zero overshoot on identity parts.

**Anchors:** shared center.

**Risks:** parts off a common origin read as flung.

**Forbidden shortcuts:** never fix occlusion with `z-index`.

### SEP-03 — Depth-layered separation

**Intent:** depth without 3D geometry.

**Layers:** four to twelve shadow-able parts.

**Motion:** separate along depth, near parts first.

**Timing:** 0.8–1.4 s, 30–50 ms stagger.

**Easing:** `settle`; blur at most about 4 px.

**Anchors:** part center, `transform-box: fill-box`, `transform-origin: center`.

**Risks:** whole-group blur reads as focus pull; cost above 12 parts.

**Limits:** Lottie exposes no blur primitive (`observed`); use scale, opacity, tint.

### SEP-04 — Occlusion-order assembly

**Intent:** reveal order for a multi-part mark.

**Layers:** every part with recorded z-order.

**Motion:** derive order from the overlap graph; back layers first.

**Timing:** 0.8–1.4 s, 60–120 ms stagger.

**Easing:** `settle`, opacity 0→1, `translateY` 12 px→0, scale 0.96→1.

**Anchors:** part centers; keep one visible.

**Risks:** mutual containment, which is impossible.

**Limits:** author a hand-over-coin sandwich explicitly.

### SEP-05 — Slice and shatter separation

**Intent:** signal data or cyberpunk.

**Layers:** N copies of one mark, one `clipPath` per slice.

**Motion:** shift slice i by `(i − N/2) × 18 px`; inset clip rects 0.5 px for a seam.

**Timing:** 0.6–1.0 s, 30 ms stagger.

**Easing:** `snap` grid-locked, `settle` back.

**Anchors:** canvas centerline; symmetric offsets.

**Risks:** uneven slice widths, mismatched seams.

### SEP-06 — Mask separation on flattened art

**Intent:** deconstruct one flat PNG without per-part source.

**Layers:** N identical image copies clipped to a band or conic wedge.

**Motion:** translate each copy along its own direction.

**Timing:** 0.6–1.0 s out and back.

**Easing:** `settle`; keep band ramps linear.

**Anchors:** the image center.

**Risks:** hard band edges at 100%, gradient banding, no hidden detail.

**Forbidden shortcuts:** never measure per frame; bake the numbers once.

## Depth without 3D

Map normalized depth `z` in `[-1, 1]`, 0 the logo plane:

```text
channel   mapping                      value at |z| = 1
scale     1 − 0.22 × |z|               0.78
blur      2.5 × |z| px                 2.5 px
opacity   1 − 0.55 × |z|               0.45
shadow    (0, 6 × z) px, alpha 0.28|z|  6 px at 0.28 alpha
```

Paint far parts first. Never blur a whole group; that is a focus pull, not depth. Count per-part blur as a per-frame rasterization cost; hold parts near 12. Grouping properties — `opacity` below 1, `filter`, `clip-path`, `mask`, non-visible `overflow` — flatten the 3D context, so `translateZ` and `opacity` cannot share one element; nest them.

## Ordering rules

Derive reveal order from z-order and overlap, then topologically sort the graph so background layers precede every mark. SVG paints in document order, so correct occlusion by reordering the DOM per frame or by clipping a background-colored copy of the front parts above the back. Flag mutual containment for a manual override; it is impossible. Apply FLIP only between DOM layouts; inside SVG coordinates are known.

## Frame contract

Use half-open intervals `[start, start + duration)`, 30 fps:

```text
0–6      establish
6–36     outbound leg
36–60    hold at separation
60–90    mirrored return leg
90–119   canonical hold
```

Make the return leg the exact reverse of the outbound leg, easing inverted, no re-timing; any other pairing pops.

## Limits

- Wordmarks, where slices cut letters into illegible fragments.
- Marks never designed as separable parts.
- Parts sharing one background plate, which travel as one unit.
- Separation exposing unapproved hidden overlaps.

## Failure modes

### Canvas-origin shrink

**Symptom:** parts drift inward as they scale; the mark collapses.
**Repair:** set `transform-box: fill-box` and `transform-origin: center`.

### Occlusion inverts

**Symptom:** a front mark passes behind a back layer.
**Repair:** re-sort the DOM per frame or clip a background-colored front part.

### Depth reads as focus pull

**Symptom:** the mark goes soft as a whole; nothing recedes.
**Repair:** blur per part; confirm far parts arrive first.

### Raster seams

**Symptom:** hard seams or tonal bands appear between slices.
**Repair:** equalize slice widths, inset clip rects 0.5 px.

## QA

- Confirm bounds, centroid, and z-order for every part.
- Verify no unapproved occlusion at 25%, 50%, 75%, and 100%.
- Compare the reassembled poster frame to the master.
- Inspect seams on white, black, checkerboard, and the brand colour taken from the profiled `palette`.
- Measure render time and memory near the 12-part ceiling.
- Confirm the reduced-motion asset is a static final frame.

Depth figures stay provisional until measured; re-check the Lottie blur gap per player version.
