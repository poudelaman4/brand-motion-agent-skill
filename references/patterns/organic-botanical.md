# Organic and Botanical Patterns

## Contents

- ORG-01 Bud to bloom
- ORG-02 Line-grown botanical
- ORG-03 Breathing growth loop
- Layer planning
- Timing and easing
- Failure modes
- QA

## ORG-01 — Bud to bloom

**Intent:** communicate emergence, growth, learning, renewal, or calm confidence.

**Layers:** rear leaves, side leaves, inner leaves, lower sepals, center petal/seed, B or monogram, wordmark, optional static rules.

**Motion:** establish the center or seed, unfurl leaves around real roots, then resolve the wordmark while the outer gesture is still readable. Mirror left/right motion only when the source geometry is genuinely symmetrical.

**Timing:** 1.8–3.0 s for a detailed mark; up to 4.0 s is reasonable when a wordmark must read one letter at a time. Keep 500–1000 ms of final hold.

**Easing:** `organic` with 0–5% temporary overshoot; use `enter` for opacity and color. Identity-critical B and wordmark should have zero overshoot.

**Anchors:** leaf root/base, vein junction, petal base, flower center. Never use the geometric center of a petal unless the artwork explicitly pivots there.

**Risks:** leaf count changes, rubbery edges, collisions, accidental asymmetry, center overlap holes, a wordmark that competes with the bloom.

## ORG-02 — Line-grown botanical

**Intent:** communicate craft, growth, or hand-made care.

**Layers:** stem/path, leaf outlines, leaf fills, veins, flower center, wordmark.

**Motion:** draw the structural path, hand off outline to fill, reveal veins, then close the flower and lock the wordmark.

**Timing:** 1.4–2.2 s; path 0–1100 ms, fills 700–1500 ms, lockup 1100–1800 ms.

**Easing:** `draw` for path reveal, `enter` for fill handoff. Do not use a fake handwriting filter on an approved geometric logo.

**Risks:** visible stroke caps, broken path continuity, raster-trace artifacts, inconsistent stroke weight, veins that appear after the final silhouette is already expected.

## ORG-03 — Breathing growth loop

**Intent:** keep a living brand mark present without a distracting story.

**Motion:** scale 1–2% and rotate no more than about 2° through a 3–6 s cycle, with a rest point at each end. Use only when the deployment context supports ambient motion.

**Risks:** distraction, battery cost, no reduced-motion equivalent, loop boundary discontinuity, visual fatigue in repeated UI use.

## Layer planning

1. Identify the visual hierarchy and lock the center/seed if it carries the identity.
2. Separate back leaves from front petals and record z-order.
3. Use a small number of meaningful groups; do not animate every vein independently.
4. Start the wordmark once two to four leaf groups are legible, unless the wordmark is the hero.
5. Preserve the final silhouette and color exactly.

## Timing and easing

A generic 4-second 30 fps organic lockup can use:

```text
0–30    core/seed establishes
4–34    outer groups begin
13–45   inner groups follow
22–54   lower groups settle
30–64   wordmark enters in parallel
48–74   descriptor/rule settles
75–96   remove temporary motion
96–119  canonical hold
```

Treat this as a starting frame contract, not a law. Adjust to the actual source and inspect the result at thumbnail size.

## Failure modes

- Starting every element at zero scale makes fine petals disappear.
- Rotating around the image center makes leaves float.
- Uniform spring bounce turns a refined identity into a toy animation.
- A large radial glow hides the logo's contours and creates banding.
- A separate reveal for every letter feels like a loading screen.
- A white matte accidentally becomes part of the transparent master.

## QA

- Compare final composite to the approved master.
- Check each leaf root, overlap, and z-order at 25%, 50%, 75%, and 100%.
- Inspect on white, black, checkerboard, and a saturated brand colour taken from the profiled `palette`.
- Review at 32, 64, 128 px, and actual delivery size.
- Confirm no temporary guide, blur, or opacity remains in the final hold.
- Confirm the reduced-motion version is immediately recognizable.
