# Logo Animation Taxonomy

Use independent axes. A logo's structure, story, context, mode, runtime, background, and platform are different decisions.

## Contents

- Classification model
- Anatomy categories
- Narrative archetypes
- Context modifiers
- Mode/runtime/background/platform
- Selection rules
- Technique families
- Scenario index

## Classification model

Record a classification before choosing a motion technique:

```text
Anatomy: organic | geometric | monogram | lettermark | wordmark | badge | combination
Narrative: trace | separate | assemble | unfold | mask | morph | sweep | route | stamp | state-change | loop
Context: premium | heritage | technology | playful | wellness | corporate | sport | luxury | friendly | precision | editorial | education | general
Register: the brand personality cell the motion must answer to
Frequency: rare | occasional | daily | frequent | keyboard
Deliverable: broadcast | product-ui | social | presentation | physical | interactive | system
Craft: light | depth | camera | pace
Mode: audit | plan | produce | interactive
Behavior: one-shot | loop | idle | state-change | ambient | scrub
Runtime: Remotion | SVG | Lottie | dotLottie | After Effects | other
Background: alpha | white | brand | dark | checkerboard-preview
Platform: web | social | editorial | app | presentation | broadcast
```

`Combination` means a symbol paired with a wordmark, descriptor, or lockup; route its symbol and text through the relevant anatomy references. `Wellness` usually uses organic or minimal guidance. `Mode` says what the agent is doing; `Behavior` says what the audience experiences. `Idle` is a rest state plus a duty cycle and is a separate decision from `loop`, which is a full cycle with no rest. Do not treat runtime, background, or platform as a motion concept.

## Anatomy categories

### Organic/botanical

Leaves, petals, flowers, branches, waves, droplets, or forms anchored to a root, base, vein, or natural growth direction. Read `patterns/organic-botanical.md`.

### Geometric/constructive

Circles, polygons, grids, bars, blocks, lines, or modular shapes. Read `patterns/geometric-constructive.md`.

### Monogram and lettermark

A single initial, interlocked initials, or a compact letter-based identifier. Read `patterns/monogram-and-lettermark.md`.

### Wordmark and lockup

Typography-led identity or a symbol paired with a name and descriptor. Read `patterns/wordmark-and-lockup.md`.

### Badge and emblem

A contained composition with rings, seals, ribbons, borders, crests, or dense detail. Read `patterns/badge-and-emblem.md`.

## Narrative archetypes

| Archetype | Best use | Typical range | Main risk |
|---|---|---:|---|
| Trace | Defined outline, stroke, or path | 0.8–2.2 s | Hairlines disappearing or caps looking wrong |
| Assemble | Separate modules converge | 0.9–1.8 s | Loading-spinner feeling or collisions |
| Unfold | Leaves, petals, panels, or pages open | 1.2–3.0 s | Incorrect pivots or rubbery overshoot |
| Mask | Typography or icon revealed through a boundary | 0.6–1.4 s | Arbitrary clipping direction |
| Separate | Independently addressable parts move apart and reassemble | 0.7–2.0 s | Wrong occlusion order or a wordmark cut into fragments |
| Morph | Compatible source and target geometry | 1.0–2.0 s | Self-intersection or topology changes |
| Sweep | Gradient, foil, or light pass across a readable mark | 0.4–0.8 s | Banding in 8-bit alpha or competing with the mark |
| Route | A packet, line, or accent follows a meaningful path | 0.9–1.8 s | Generic glow or visual spaghetti |
| Stamp/seal | Short, decisive press or closure | 0.5–1.0 s | Cartoon aggression or illegible microtype |
| State change | Hover, active, success, or progress state | 90–180 ms | State semantics or accessibility mismatch |
| Loop | Ambient brand behavior | 3–8 s | Distraction or boundary discontinuity |

These are planning ranges, not a reason to force complexity onto a simple mark. Use the canonical motion tokens and the user's duration when specified.

## Context modifiers

- **Premium/minimal:** fewer gestures, clean easing, no particles, no default bounce, generous hold.
- **Education/LMS:** communicate growth, knowledge, progress, or completion; avoid childish clichés and false state claims.
- **Playful/character:** one intentional spring or gesture; do not make every letter bounce independently.
- **Technology/software:** use structure, routing, or modular logic; avoid unexplained neon and generic network effects.
- **Wellness/organic:** favor breath, unfurl, and continuity; keep motion calm and provide a resting final state.
- **General:** choose the simplest concept that explains the mark's structure.

`Register` is a veto list, not a preference: it removes techniques outright. `Frequency` scales the register's duration, gesture, and overshoot ceilings. `Deliverable` decides which delivery reference binds. Read `taste/brand-register.md` and `technique-selection.md`.

## Mode, runtime, background, and platform

- **Audit:** report source capability, risks, and missing information; no implementation by default.
- **Plan/storyboard:** brief, layer inventory, manifest, milestones, and acceptance checks; no render by default.
- **One-shot intro:** final hold required.
- **Loop:** first and last states, velocity, color, and loop semantics must match.
- **Interactive:** short state transitions with keyboard, focus, and reduced-motion equivalents.
- **SVG/Lottie/dotLottie:** prefer named vector groups, masks, trim paths, and explicit state definitions.
- **After Effects/Remotion:** use deterministic keyframes/frame functions and verify the final encoded output.
- **Transparent:** keep alpha separate from the white/opaque fallback.
- **White background:** exact `#FFFFFF` only when requested; never bake it into the alpha master.
- **Platform:** recompose deliberately for square, vertical, horizontal, app, editorial, and broadcast targets.

## Technique families

Group candidate techniques by role before ranking them. Exactly one `reveal` technique can be primary; `surface`, `loop`, `driver`, and `a11y` are additive and never compete for the primary slot.

| Role | Families |
|---|---|
| Reveal | line drawing, kinetic typography, mask or wipe, circular sweep, matter dissolve, morph |
| Transform | separation, geometric construction, depth extrusion, elastic settle |
| Surface | gradient and light sweep |
| Loop | idle and ambient, orbit and rotor |
| Driver | scroll and scrub linkage |
| Accessibility | reduced-motion branch, emitted unconditionally |

Resolve collisions by keeping the highest-scoring reveal as primary and demoting the rest. Read `technique-selection.md` for the capability ladder, the gate codes, and the evidence rules that produce this ranking.

## Selection rules

1. If the source has no reliable layers, choose a grouped or whole-mark concept before attempting independent motion.
2. Run the structural profile before choosing. A technique the profile gated is impossible with this source, not merely inelegant.
3. If the mark is identity-critical, prefer transforms and opacity over redraw, morph, or texture.
4. Choose one primary narrative and make every secondary gesture support it.
5. Start the wordmark once the primary silhouette is readable unless text is explicitly the hero.
6. Test the concept at thumbnail size and on the final background.
7. Reject a concept that needs a long explanation to look intentional.
8. For frame-driven renderers, use half-open intervals `[start, start + duration)` and guarantee a static hold after `settle_frame`.

## Scenario index

| ID | Scenario | Reference |
|---|---|---|
| ORG-01 | Bud to bloom | `patterns/organic-botanical.md` |
| ORG-02 | Line-grown botanical | `patterns/organic-botanical.md` |
| ORG-03 | Breathing growth loop | `patterns/organic-botanical.md` |
| GEO-01 | Trace to solid | `patterns/geometric-constructive.md` |
| GEO-02 | Modular assembly | `patterns/geometric-constructive.md` |
| GEO-03 | Compatible reconfiguration | `patterns/geometric-constructive.md` |
| MON-01 | Interlace/weave | `patterns/monogram-and-lettermark.md` |
| MON-02 | Counter reveal | `patterns/monogram-and-lettermark.md` |
| MON-03 | Seal press | `patterns/monogram-and-lettermark.md` |
| LTR-01 | Controlled modular build | `patterns/monogram-and-lettermark.md` |
| LTR-02 | Outline to solid | `patterns/monogram-and-lettermark.md` |
| LTR-03 | Initial to descriptor | `patterns/monogram-and-lettermark.md` |
| WORD-01 | Tracking settle | `patterns/wordmark-and-lockup.md` |
| WORD-02 | Directional mask | `patterns/wordmark-and-lockup.md` |
| WORD-03 | Write-on | `patterns/wordmark-and-lockup.md` |
| WORD-04 | Mark-to-lockup | `patterns/wordmark-and-lockup.md` |
| BADGE-01 | Seal construction | `patterns/badge-and-emblem.md` |
| BADGE-02 | Stamp press | `patterns/badge-and-emblem.md` |
| BADGE-03 | Ribbon or controlled orbit | `patterns/badge-and-emblem.md` |
| EDU-01 | Concept-to-symbol | `contexts/education-and-lms.md` |
| EDU-02 | Progress to completion | `contexts/education-and-lms.md` |
| EDU-03 | Knowledge network | `contexts/education-and-lms.md` |
| EDU-04 | Compact LMS state | `contexts/education-and-lms.md` |
| PREM-01 | Hairline trace | `contexts/premium-and-minimal.md` |
| PREM-02 | Quiet lockup | `contexts/premium-and-minimal.md` |
| PREM-03 | Restrained foil sweep | `contexts/premium-and-minimal.md` |
| PLAY-01 | Spring reveal | `contexts/playful-and-character.md` |
| PLAY-02 | Squash and stretch | `contexts/playful-and-character.md` |
| PLAY-03 | Gesture or celebration | `contexts/playful-and-character.md` |
| TECH-01 | Node assembly | `contexts/technology-and-software.md` |
| TECH-02 | Data trace | `contexts/technology-and-software.md` |
| TECH-03 | Circuit routing | `contexts/technology-and-software.md` |
| TECH-04 | Interactive state | `contexts/technology-and-software.md` |
| LINE-01 | Continuous contour draw-on | `patterns/line-drawing-and-trace.md` |
| LINE-02 | Multi-stroke trace with junction order | `patterns/line-drawing-and-trace.md` |
| LINE-03 | Contour and edge trace | `patterns/line-drawing-and-trace.md` |
| LINE-04 | Draw-then-fill | `patterns/line-drawing-and-trace.md` |
| LINE-05 | Travelling dash and comet | `patterns/line-drawing-and-trace.md` |
| LINE-06 | Per-letter write-on | `patterns/line-drawing-and-trace.md` |
| SEP-01 | Radial burst separation | `patterns/separation-and-explode.md` |
| SEP-02 | Axis separation and reassembly | `patterns/separation-and-explode.md` |
| SEP-03 | Depth-layered separation | `patterns/separation-and-explode.md` |
| SEP-04 | Occlusion-order assembly | `patterns/separation-and-explode.md` |
| SEP-05 | Slice and shatter separation | `patterns/separation-and-explode.md` |
| SEP-06 | Mask separation on flattened art | `patterns/separation-and-explode.md` |
| KINE-01 | Per-glyph stagger | `patterns/kinetic-typography.md` |
| KINE-02 | Baseline mask reveal | `patterns/kinetic-typography.md` |
| KINE-03 | Variable-axis weight morph | `patterns/kinetic-typography.md` |
| KINE-04 | Text on a path | `patterns/kinetic-typography.md` |
| KINE-05 | Initial to lockup | `patterns/kinetic-typography.md` |
| IDLE-01 | Rest to breathing loop | `patterns/idle-and-ambient.md` |
| IDLE-02 | Orbit and rotor idle | `patterns/idle-and-ambient.md` |
| IDLE-03 | Interactive state set | `patterns/idle-and-ambient.md` |
| IDLE-04 | Scroll and scrub linkage | `patterns/idle-and-ambient.md` |
| FX-01 | Particle assemble | `patterns/matter-and-particles.md` |
| FX-02 | Alpha-threshold dissolve | `patterns/matter-and-particles.md` |
| FX-03 | Turbulence displacement | `patterns/matter-and-particles.md` |
| FX-04 | Halftone and dot-matrix build | `patterns/matter-and-particles.md` |
| FX-05 | Glitch and RGB split | `patterns/matter-and-particles.md` |
| PROFILE-01 | Profile and rank techniques | `technique-selection.md` |
| MECH-01 | Cross-renderer advanced mechanics | `implementation/advanced-mechanics.md` |
