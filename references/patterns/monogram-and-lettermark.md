# Monogram and Lettermark Patterns

## Contents

- MON-01 Interlace/weave
- MON-02 Counter reveal
- MON-03 Seal press
- LTR-01 Controlled build
- LTR-02 Outline to solid
- LTR-03 Initial to descriptor
- Typography safeguards
- QA

## MON-01 — Interlace/weave

**Intent:** reveal initials as a connected mark while preserving over/under logic.

**Layers:** first character, second character, overpass, underpass, counters, optional ring.

**Motion:** establish the first character, add the second, then pass one stroke over and under through a matte.

**Timing:** 1.0–1.8 s; initial 0–550 ms, second 350–1000 ms, weave 700–1300 ms, seal 1100–1500 ms.

**Risks:** unreadable initials, incorrect occlusion, braid-like motion, changing stroke weight.

## MON-02 — Counter reveal

**Intent:** make a compact initial feel crafted and legible.

**Motion:** begin with a terminal or dot, draw the skeleton, then fill while keeping counters open.

**Timing:** 0.8–1.4 s; terminal 0–250 ms, outline 150–800 ms, fill 550–1100 ms.

**Risks:** counters fill prematurely, stems merge, monogram becomes ambiguous at small sizes.

## MON-03 — Seal press

**Intent:** give a monogram a decisive, premium stamp.

**Motion:** a short scale-down from 103–105% to 100%, with little or no rotation and no bounce.

**Timing:** 0.5–0.9 s; impact 0–250 ms, settle 250–550 ms, hold 300–800 ms.

**Risks:** cartoon impact, motion blur, perceived aggression, muddy small details.

## LTR-01 — Controlled modular build

Build a standalone initial from a small number of strokes or shapes. Use 40–60 ms group stagger, stable silhouette, and zero overshoot. Avoid a loading-icon look.

## LTR-02 — Outline to solid

Draw the structural outline, then solidify without disturbing counters. Use `draw` followed by `enter`; test every frame around negative space.

## LTR-03 — Initial to descriptor

Stabilize the initial first, then add a descriptor or full name. Keep the initial dominant and preserve the approved lockup spacing.

## Typography safeguards

- Use approved outlines or embed the exact font.
- Keep language-specific glyphs and reading direction intact.
- Do not animate individual letters when the font has fragile joins or the brand calls for quiet typography.
- If letters are independently extracted, verify optical spacing rather than trusting bounding boxes.
- Use a baseline or cap-height anchor for vertical entrances.

## QA

- Identify the initials at the midpoint and final frame.
- Confirm counters remain open at every checkpoint.
- Confirm over/under order never flips accidentally.
- Compare final kerning, weight, and clear space to the master.
- Test 16, 32, 64, and 128 px previews.
- Confirm no descriptor enters before the mark is readable unless the concept intentionally makes text primary.
