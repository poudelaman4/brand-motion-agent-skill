# Geometric and Constructive Patterns

## Contents

- GEO-01 Trace to solid
- GEO-02 Modular assembly
- GEO-03 Compatible reconfiguration
- Geometry rules
- Timing
- QA

## GEO-01 — Trace to solid

**Intent:** reveal a precise outline, then give it weight without changing its identity.

**Layers:** outline path, fill shape, counter/cutout masks, optional wordmark.

**Motion:** draw the structural outline, hand off to the solid fill, preserve negative space, and hold.

**Timing:** 0.8–1.4 s; trace 0–800 ms, fill 500–1100 ms, hold 400–700 ms.

**Easing:** `draw` followed by `settle` or `enter`. Keep line caps and joins consistent with the source.

**Risks:** thin strokes disappearing, fill covering counters, a trace that suggests a different shape, antialiasing flicker.

## GEO-02 — Modular assembly

**Intent:** communicate systems, structure, technology, or progress.

**Layers:** three to six major modules, connectors, negative-space pieces, optional grid guides, final lockup.

**Motion:** modules converge on the approved grid with a 40–70 ms stagger. Remove construction guides after the lock.

**Timing:** 0.9–1.6 s; assembly ends by about 1200 ms; hold 500–900 ms.

**Easing:** `snap` for grid-locked pieces, `settle` for final alignment. Use zero overshoot on identity-critical geometry.

**Risks:** loading-spinner feeling, collisions, late micro-adjustment, gaps changing at small sizes.

## GEO-03 — Compatible reconfiguration

**Intent:** show a meaningful change from one stable configuration into another.

**Layers:** source modules, target modules, masks, connectors.

**Motion:** morph only when path topology and point order are compatible. Otherwise use a masked crossfade or assembly.

**Risks:** self-intersection, tangencies, rasterized edges, point-order mismatch, a final state that is not exactly the approved target.

## Geometry rules

- Use the original grid and clear space.
- Do not stretch circles, rounded rectangles, or custom letterforms to fit a composition.
- Keep a fixed camera and alternate layout rules for each aspect ratio.
- Use masks and counters as first-class layers.
- Keep at least one visible anchor during assembly so the mark remains recognizable.

## Timing

For a simple mark, do not add complexity to fill a duration. A 4-second sequence is justified only when the user requests a ceremonial intro or the wordmark has a meaningful sequential role. Record the reason in the motion brief.

## QA

- Inspect every checkpoint for collisions and tangencies.
- Compare the final frame to the vector master, not only to a previous render.
- Test at small sizes where thin strokes and counters disappear.
- Confirm no construction grid or snap indicator remains.
- Verify all alternate aspect ratios independently.
- Confirm the mark is recognizable before the wordmark finishes.
