# Technique Selection Algorithm

Read a logo's structure, decide which motion techniques are physically possible, and rank the ones that fit. Run this between locking the source and choosing a concept so the recommendation is evidence, not a prior.

## Contents

- How to use this
- Capability ladder
- Feature fingerprint
- Feasibility gates
- Evidence rules
- Conflict resolution
- Recommendation output
- Draw-on ordering
- Limits

## How to use this

```bash
# --register is required. Taste is a judgement about the brand, not a property of
# the file, so the profiler refuses to guess it.
python scripts/profile_logo.py path/to/logo.svg --register premium
python scripts/profile_logo.py path/to/logo.png --register corporate --frequency daily
python scripts/profile_logo.py path/to/logo.svg --register heritage --draw-plan
```

The register is the one input the profiler cannot derive. Take it from a stated brand claim or an explicit user answer, label the inference `inferred`, and never infer it from the asset's structure: a mark's geometry says nothing about whether the brand is playful or institutional.

The profiler reports `observed` for anything it measures directly from the file, `inferred` for anything it derives, and `provisional` for anything it estimates. It never emits `observed` for a recommendation: a ranked technique is always `inferred`, and on a flattened raster always `provisional` because connected components are evidence, not layers.

Treat the output as a ranked shortlist, not a decision. Reject a recommendation that the brand context forbids and record the reason. Keep the profiler's feasibility gates: a technique listed under `blocked` is not a stylistic mismatch, it is impossible with this source.

## Capability ladder

Rate the source before rating any technique. Each rung unlocks a family; a technique is only possible when its rung is present.

```text
R0  bitmap            image element, background-image, flattened PNG
R1  vector primitives circle, rect, ellipse, line, polyline, polygon
R2  single path       one or more subpaths in a d attribute
R3  layered vector    sibling shapes, groups, ids or classes
R4  stroked vector    stroke, stroke-width, stroke-linecap, stroke-linejoin
R5  paint servers     gradients, patterns, mask, clipPath, filter
R6  outlined text     one path per glyph
R7  live text         text or textPath elements
R8  runtime           Lottie, dotLottie, Remotion, GSAP, Rive
```

Map rungs to families: R2 unlocks draw-on and mask work. R3 unlocks separation and choreography. R4 unlocks junction handling and draw-then-fill. R5 unlocks matter effects. R7 unlocks variable-axis typography. R8 unlocks interactive and state-machine behavior.

R0 and R1 permit only whole-mark fades, wipes, splits, and filters. Recommend a layer or vector source before recommending anything on those rungs.

## Feature fingerprint

Measure these before scoring. The profiler emits them; the thresholds below are the working bands.

```text
open_len_ratio     open subpath length / total length        draw-on candidate above 0.40
stroke_present     any resolved stroke paint                 draw-on needs this
stroke_width_norm  median stroke width / bbox diagonal       legible band 0.015–0.12
hole_count         counters resolved per fill rule            lettermark signal at 2 or more
component_count    connected components above the area floor  separation needs 2 or more
all_disjoint       no component touches another               separation needs this
sym_rot_k          detected rotational order                  sweep and orbit need 3 or more
sym_mirror         mirror score in 0..1                       symmetry at 0.85 or more
aspect             long side / short side                    wordmark above 3.0
complexity         composite 0–100 score                      bands below
ink_ratio          alpha coverage of the frame               mask work needs 0.01–0.97
color_count        distinct quantized colors                  sweep needs 2 or more
```

Read complexity as a band, not a number:

| Score | Band | Prefer |
|---:|---|---|
| 0–20 | atomic | geometric construction, orbit, idle loop, circular sweep |
| 20–38 | geometric | mask wipe, separation, geometric construction |
| 38–55 | moderate | line drawing, separation, kinetic typography |
| 55–72 | detailed | kinetic typography, line drawing, gradient sweep |
| 72–100 | illustrative | matter effects, morph, progressive mask |

Complexity never justifies adding work to a simple mark. A triangle scored 8 should get a wipe, not a particle system.

## Feasibility gates

Gates are absolute, not penalties. Each produces a `blocked_by` entry with a code, a detail string, and a remedy. A gated technique is omitted from the ranking entirely and reported under `blocked` with its reason.

| Code | Condition | Blocks | Remedy |
|---|---|---|---|
| `NO_VECTOR_GEOMETRY` | zero drawable shapes | line drawing, kinetic type, morph, geometric construction | supply SVG, or vectorize and accept traced fidelity |
| `TRACED_GEOMETRY` | contours came from tracing | line drawing, kinetic type | use mask wipe or matter effects |
| `LIVE_TEXT` | `text` present and not outlined | line drawing, kinetic type | convert text to outlines |
| `EVENODD_FILL_RULE` | counters are parity-managed | line drawing, kinetic type, morph | normalize to nonzero winding with opposite hole orientation |
| `DEGENERATE_SILHOUETTE` | ink ratio outside 0.01–0.97 | mask wipe, circular sweep, matter | re-crop with padding |
| `SINGLE_COMPONENT` | fewer than 2 components | separation | use mask wipe, sweep, or orbit |
| `MONOLITHIC_MASS` | largest component above 0.995 of ink | separation, matter | use mask wipe or line drawing |
| `MONOCHROME` | one color and no gradient | gradient sweep | use mask wipe or geometric construction |
| `BROKEN_USE_REF` | `use` points at a missing id | every technique | fix the ids in the source |
| `FILTERED_COMPOSITE` | filter, mask, or clip present | line drawing, kinetic type | flatten filters, or accept mask work on the raster |
| `SHADED_ARTWORK` | painted shading on traced geometry | geometric construction, separation | use gradient sweep or mask wipe |

Never work around a gate by silently degrading the technique. Either resolve the gate with the stated remedy or record the technique as `blocked` in the brief.

## Evidence rules

Each rule is a predicate over the fingerprint that adds or removes evidence in `[-0.30, 0.50]`. Positive rules are the technique's case for existing; negative rules are its case against. Grouped by the family they serve.

```text
R01  line_draw_on          open_len_ratio > 0.40 AND stroke_present            +0.45
R02  line_draw_on          open_subpath_count >= 2 AND openness > 0.25          +0.20
R03  line_draw_on          stroke_width_norm BETWEEN 0.015 AND 0.12            +0.15
R04  line_draw_on          round caps are the majority                          +0.10
R05  line_draw_on          monoline, constant stroke width                      +0.15
R06  line_draw_on          mean curvature < 0.15 AND corner share < 0.20        +0.10
R07  line_draw_on          open_len_ratio < 0.05 AND fill_present               -0.30
R08  line_draw_on          edge density above 0.42                              -0.20
R09  line_draw_on          node total above 900                                 -0.15
R10  kinetic_typography    wordmark detected AND letter_count >= 3              +0.50
R11  kinetic_typography    baseline strength > 0.35 AND aspect_signed > 0.55    +0.20
R12  kinetic_typography    3–14 components of near-equal height                 +0.20
R13  kinetic_typography    hole_count >= 2 AND aspect > 3.0                     +0.15
R14  kinetic_typography    complexity BETWEEN 38 AND 72                         +0.10
R15  kinetic_typography    outlined live text, no stroke, 2+ counters            +0.20
R16  separation_explode    component_count >= 5 AND all_disjoint                +0.45
R17  separation_explode    component_count >= 2 AND entropy > 0.7               +0.25
R18  separation_explode    two or more translate-only groups in the source      +0.30
R19  separation_explode    largest component below 0.55 of ink                  +0.15
R20  separation_explode    component_count < 3                                 -0.35
R21  separation_explode    centroid offset above 0.45                           +0.10
R22  mask_wipe             any silhouette AND complexity >= 20                  +0.20
R23  mask_wipe             gradient area ratio above 0.05                        +0.15
R24  mask_wipe             symmetry above 0.85                                  +0.10
R25  mask_wipe             centroid offset above 0.35 OR top-heavy              +0.10
R26  circular_sweep        sym_rot_k >= 3 AND rotational score > 0.80           +0.40
R27  circular_sweep        four or more duplicate instances per cluster          +0.25
R28  circular_sweep        aspect 0.92–1.10 AND circularity above 0.70           +0.25
R29  circular_sweep        sym_rot_k < 2                                        -0.30
R30  particle_dissolve     complexity >= 60                                     +0.25
R31  particle_dissolve     4–4096 colors AND not flat                           +0.20
R32  particle_dissolve     hole area ratio above 0.20                           +0.15
R33  particle_dissolve     complexity < 38                                      -0.35
R34  particle_dissolve     color count above 8192, photographic                 -0.20
R35  morph_shape           a second approved state exists                       +0.40
R36  morph_shape           the two states share a topology class                +0.20
R37  morph_shape           complexity > 85                                      -0.30
R38  geometric_construction  sym_rot_k >= 4                                     +0.30
R39  geometric_construction  complexity <= 20                                   +0.30
R40  geometric_construction  solidity above 0.85                               +0.15
R41  geometric_construction  vertex density below 4                             +0.10
R42  gradient_sweep        gradient_count >= 1                                 +0.35
R43  gradient_sweep        gradient area ratio above 0.15                       +0.25
R44  gradient_sweep        color count >= 3                                      +0.15
R45  gradient_sweep        soft shading present                                 +0.20
R46  extrusion_3d          complexity 20–55 AND solidity > 0.80                  +0.30
R47  extrusion_3d          stroke-to-size ratio above 0.15                      +0.15
R48  extrusion_3d          hole count >= 3                                       -0.20
R49  bounce_elastic        source uses translate AND complexity <= 55            +0.20
R50  bounce_elastic        symmetry above 0.80                                  +0.10
R51  orbit_rotate          sym_rot_k >= 2                                        +0.35
R52  orbit_rotate          aspect 0.90–1.12                                      +0.15
R53  orbit_rotate          quadrant entropy above 0.85                           +0.15
R54  orbit_rotate          quadrant entropy below 0.55                          -0.25
R55  idle_loop             complexity <= 38 AND symmetry > 0.55                  +0.30
R56  idle_loop             the source already authors a dash pattern            +0.20
R57  idle_loop             complexity > 72                                      -0.20
R58  scroll_scrub          aspect > 2.4                                          +0.20
R59  scroll_scrub          semantic layer naming includes a wordmark             +0.25
```

Then apply three global haircuts, in order:

1. If symmetry detection is ambiguous, multiply every symmetry-driven rule by 0.5.
2. If style resolution was partial because CSS could not be resolved, subtract 0.10 from every score.
3. If overall confidence is below 0.55, subtract 0.20 from every score.
4. If the geometry is traced rather than authored, halve every score. Traced contours are not the design.

## Conflict resolution

Score is not a ranking until the family collisions are resolved. Group techniques by role: `reveal`, `transform`, `surface`, `loop`, `driver`, `a11y`.

1. Exactly one `reveal` technique may be primary. Keep the highest scorer; demote the rest to supporting or drop them.
2. `surface`, `loop`, `driver`, and `a11y` are additive. They never compete and never count as supporting gestures.
3. A supporting gesture must reinforce the primary. If a supporting technique's evidence does not reference a structural feature the primary also uses, drop it.
4. Keep at most one primary plus two supporting gestures. A short reveal combining trace, bounce, glitch, particles, camera movement, and 3D is rejected outright.
5. Emit the reduced-motion branch unconditionally. It is never a candidate and never competes.
6. If every `reveal` technique is gated, fall back to the whole-mark mask wipe and record why each alternative was gated. A whole-mark fade is `observed`-safe and always available; a fabricated layer structure is not.

## Recommendation output

```text
profile          fingerprint values actually measured
capability       the source's rung and the families it unlocks
recommendations  ranked list of one primary plus up to two supporting
blocked          technique, gate code, detail, remedy
draw_plan        per-path draw ranges when line drawing wins
notes            conflicts resolved and haircuts applied
```

Each recommendation carries the scenario id, the technique key, a score, the rules that fired with their weights, and a confidence of `inferred` or `provisional`. Map the scenario id into `taxonomy.md`'s scenario index so the recommendation is expressible in the existing brief and manifest vocabulary.

Keep the fired rules in the output. A recommendation an agent cannot explain is a recommendation the user will reject.

## Draw-on ordering

When line drawing wins, derive the order from the geometry rather than inventing it.

1. Build an endpoint graph from every subpath's two endpoints. Cluster endpoints within a small fraction of the bbox diagonal into single vertices.
2. Count odd-degree vertices. Zero means an Eulerian circuit and the mark can be drawn from any point; two means an Eulerian path that must start at one of them; more than two forces at least one pen lift, and each lift needs its own timing gap.
3. Choose each start point in priority order: a free degree-one endpoint first, then 12 o'clock clockwise for a closed mark, then reading direction for an open mark. Never start at a junction, where two caps coincide at frame 0.
4. If the mark is mirror-symmetric about an axis and closed, do not start on that axis; it leaves a visible seam. Draw mirrored halves from the apex instead.
5. Normalize duration by length when strokes should read as one pen at constant speed: duration is proportional to path length at a fixed speed. Use a designed sequence instead when the reveal should feel authored, and cap any pen-lift gap at about 250 ms.
6. Emit per path a start fraction, an end fraction, a delay, and a duration. Read `patterns/line-drawing-and-trace.md` for the dash arithmetic and the junction handling.

## Limits

Do not treat the fingerprint as the decision. It measures structure, and structure is only one of three inputs: the brand context modifier, the narrative the brand is already telling, and the target player. A premium mark can score 0.60 for gradient sweep and still be wrong.

Do not profile a source that has not been locked. A profile of the wrong variant produces confident recommendations for artwork that will never ship.

Do not report a `provisional` recommendation from a flattened raster as though it were observed. On a raster, component counts, holes, and symmetry are estimates; say so in the brief.

Do not let a high score raise the complexity of a simple mark. The bands exist so an 8-point triangle gets a wipe.

Do not skip the capability ladder because a technique looks good. A masked or filtered composite reports a silhouette that is not its path geometry, and draw-on against it produces a wrong result that still validates.
