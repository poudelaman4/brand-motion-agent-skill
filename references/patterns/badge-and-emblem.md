# Badge and Emblem Patterns

## Contents

- BADGE-01 Seal construction
- BADGE-02 Stamp press
- BADGE-03 Ribbon or controlled orbit
- Detail strategy
- Timing
- QA

## BADGE-01 — Seal construction

**Intent:** communicate heritage, membership, achievement, or institutional trust.

**Motion:** draw the outer ring, resolve the central icon, reveal curved type or banner elements, and close the inner border.

**Layers:** outer ring, inner ring, central icon, curved type, separators, banner, field.

**Timing:** 1.6–2.6 s; ring 0–900 ms, icon 500–1500 ms, type 850–1900 ms, closure 1500–2200 ms.

**Easing:** `draw` for rings and rules, `settle` for modules, `enter` for type.

**Risks:** too many simultaneous actions, tiny type, incorrect curved-text baseline, upside-down text, unreadable microdetails.

## BADGE-02 — Stamp press

Use a short scale-down from 103–105% to 100%, little or no rotation, no bounce, and a clean stop.

**Timing:** 0.5–0.9 s; impact 0–250 ms, settle 250–550 ms, hold 300–800 ms.

## BADGE-03 — Ribbon or controlled orbit

Unfurl a ribbon or move one accent around a ring while curved type remains upright. Use full rotation only when the badge is rotationally symmetric.

**Risks:** upside-down text, excessive spin, ribbon collision, dizziness, distracting loop.

## Detail strategy

- Limit animated groups to three to six meaningful elements.
- Keep microtype static until its container is stable.
- Do not animate every border segment if one ring can establish the structure.
- Separate decorative effects from the canonical badge layers.
- Treat the badge center as the identity anchor unless the ring is the hero.

## QA

- Inspect at actual badge size and at thumbnail size.
- Verify curved text orientation, tracking, and baseline.
- Check all counters and inner borders at 25%, 50%, 75%, and 100%.
- Confirm temporary guides and orbit scaffolding disappear.
- Compare the final frame to the approved seal exactly.
- Confirm a static end frame works for print, press, and reduced-motion contexts.
