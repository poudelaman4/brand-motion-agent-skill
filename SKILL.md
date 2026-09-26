---
name: animation-logo-skill
description: Detect the structure of an approved logo or mark, recommend the motion techniques that structure supports, then create, storyboard, render, or QA the motion while preserving canonical geometry and the final lockup. Covers basic reveals plus advanced line drawing and stroke trace, separation and explode, kinetic typography, morph, gradient sweeps, particles, and idle loops, delivered as SVG, Lottie/dotLottie, Remotion, or transparent, white, and dark video. Trigger on requests to animate a logo or mark, to decide which animation a logo can support, or to review an existing logo animation; do not use for static logo redesign, font or glyph extraction, generic motion graphics, product animation, or format-only video conversion.
compatibility: Designed for filesystem-enabled agents. Optional Python, Pillow, NumPy, SciPy, FFmpeg, and a renderer such as Remotion may be used when available; unavailable renderers stop at the renderer-neutral brief/manifest and mark rendering blocked.
metadata:
  version: "1.3"
  category: motion-design
---

# Animation Logo Skill

Create logo motion that feels authored, not generated. Preserve the approved identity at the final frame while making the transition clear, economical, and appropriate to the brand.

## Task modes

Choose one mode before doing work:

- **Audit:** inspect the source and existing motion, report risks and missing information, and stop before implementation unless asked.
- **Plan/storyboard:** produce the concept brief, layer inventory, motion manifest, milestones, and QA plan; do not render by default.
- **Produce:** implement, render, inspect, and package the requested outputs.
- **Interactive:** define explicit runtime states and transitions for hover, press, active, selected, or reactive behavior, with reduced-motion equivalents.

If the user does not name a mode, infer it from the requested deliverables. Ask only when the answer changes whether rendering is appropriate.

## Operating contract

- Treat the approved static logo as the identity source of truth. Do not let generative imagery redraw letterforms, counters, proportions, colors, or clear space.
- Separate facts into `observed`, `inferred`, `provisional`, and `blocked`. Do not present a guess as an approved creative decision.
- Choose one primary motion idea and at most two supporting gestures. A short reveal should not combine trace, bounce, glitch, particles, camera movement, and 3D at once.
- Profile the locked source before choosing a technique, and treat the result as a shortlist rather than a decision. A detection-derived recommendation is `inferred` on a vector source and `provisional` on a flattened raster; it is never `observed`. Record a reason whenever you override it.
- Treat a gated technique as impossible rather than as a stylistic mismatch, and carry its gate code into the brief instead of silently dropping it.
- Give every non-transform channel its own manifest field. A stroke reveal, an explode vector, a true path morph, a mask wipe, and a bounded effect set are not transforms; never overload `x`, `y`, `scale`, `rotation`, or `opacity` to fake one.
- Drive every value from the frame number. A particle, noise, or scatter system is only acceptable when each value is a pure function of the frame and a stable seed, so repeated renders of the same frame range are identical.
- Keep the camera, artboard, clear space, and final lockup stable. Animate inside a fixed composition rather than repeatedly reframing the logo.
- Treat the final state as a golden state. Verify canonical geometry, text metrics, color, alpha, and clear space against the reference; use documented tolerances for encoded RGB output.
- For Remotion or other rendered video, drive every value from the frame number. Explicit state machines are allowed for interactive SVG/dotLottie runtimes.
- Never silently fabricate hidden detail when a flattened source does not contain separable layers. Offer a grouped or whole-mark fallback and state the limitation.
- Treat raster layers extracted from a flattened source as provisional reconstruction assets. A clean-looking layer can still carry low-alpha ringing or crop contamination that becomes visible during an opacity crossfade; prefer approved vector geometry for continuous rings and contours.
- One canonical motion specification and timing model may feed separate square, vertical, horizontal, alpha, white, dark, and interactive compositions. Do not regenerate each variant from scratch.

## Source capability gate

Before promising independent animation, determine whether the source is vector, layered raster, or a flattened composite.

- **Vector/layered:** semantic transforms, masks, trim paths, and compatible morphs are available if the artwork exposes them.
- **Flattened raster:** default to a whole-mark reveal, grouped masks, or manually approved groups. Independent letters, leaves, and hidden overlaps are `BLOCKED` unless the user approves a separately reconstructed asset.
- **Live text:** outline or embed the approved wordmark; do not depend on a runtime font being installed.
- **Diagnostic inspection:** `scripts/inspect_logo_assets.py` reports alpha bounds and connected components; connected components are evidence, not guaranteed semantic layers.
- **Structural profile:** `scripts/profile_logo.py` measures the source, reports its capability rung, and ranks the techniques that structure supports. Use it on vector and raster sources alike; it needs no third-party package for SVG.

## Workflow

1. **Intake:** identify the canonical source, task mode, and whether independent layer motion is mandatory. Treat other missing preferences as documented provisional defaults.
2. **Classify:** record anatomy, narrative archetype, context, mode, runtime, background, and platform. Read `references/taxonomy.md`.
3. **Lock the source:** identify approved variants, layer inventory, alpha mode, profile, resolution, and pivots. Run the inspector on raster sources.
4. **Profile and recommend:** run `scripts/profile_logo.py` on the locked source. Read the capability rung, the ranked techniques, the gated techniques and their codes, and the draw plan when line drawing is in contention. Keep at most one primary and two supporting; the brand context modifier still decides. Read `references/technique-selection.md`.
5. **Choose a concept:** select one primary pattern from the matching reference. Keep the wordmark subordinate until the mark is readable unless text is the hero. When the profile recommends something else, record why.
6. **Write the brief:** fill `assets/motion-brief-template.json`; keep the executable manifest in `assets/motion-manifest-template.json`.
7. **Storyboard:** define the opening state, two to four milestones, settle frame, final hold, reduced-motion state, and acceptance checks before coding. For a stroke reveal, derive the draw order from the endpoint graph and the Eulerian check rather than inventing it.
8. **Build:** use approved source geometry. Extract or request layers once, store tight crops with bounds, and animate transforms/opacity around semantic pivots. Do not segment per frame. Carry each technique in its own channel: dash arithmetic for a draw-on, a direction and depth for a separation, matched path pairs for a morph, a mask type and angle for a wipe. For any extracted raster crossfade, inspect the layer alone and render the exact transition midpoint before accepting it.
9. **Render variants:** derive outputs from the canonical spec using separate compositions or state definitions as needed.
10. **QA:** render exact checkpoint frames, inspect the decoded video, compare the final state to the reference, and test target players/backgrounds. For opacity crossfades, inspect direct start/mid/end stills and decode the same frames from the final file. Read `references/qa/qa-checklist.md`.
11. **Package:** deliver the source, final motion, static poster, required variants, manifest, render commands, and a pass/warn/blocked report.

## Hard blockers and provisional defaults

Only three items are hard blockers:

1. No canonical source/reference, or no way to identify the approved logo.
2. The task mode is unclear enough that producing assets could be surprising.
3. Independent layer motion is mandatory but the source cannot support it and no reconstruction is approved.

Everything else can use the defaults in `assets/motion-tokens.json` and `references/intake-and-planning.md`. Record inferred values in the brief rather than silently treating them as approvals.

## Default contract

- One-shot reveal: normally 1.2–2.4 seconds; use up to 4 seconds for a detailed organic mark or meaningful sequential wordmark.
- Rendered video: 30 fps unless specified; four seconds is 120 frames at 30 fps.
- Final hold: 500–1000 ms for an intro; indefinite for a persistent UI mark.
- Primary mark: one dominant gesture; wordmark: a quiet fade, mask, or baseline-settled stagger.
- Overshoot: 0% for identity-critical geometry; at most 5% for organic motion and at most 8% for explicitly playful accents.
- Backgrounds: keep an alpha master and provide a white or brand-color fallback when the target player is uncertain.
- Audio: silent by default; add only user-approved cues.
- Reduced motion: show the approved final state immediately, optionally with a short opacity dissolve.

## Pattern routing

Read only the references needed for the current task:

- Classification and selection: `references/taxonomy.md`
- Structure detection and technique recommendation: `references/technique-selection.md`
- Pattern feasibility by source type: `references/patterns/feasibility.md`
- Intake, defaults, and approvals: `references/intake-and-planning.md`
- Timing, easing, pivots, and layer grammar: `references/motion-foundations.md`
- Organic/botanical marks: `references/patterns/organic-botanical.md`
- Geometric/constructive marks: `references/patterns/geometric-constructive.md`
- Monograms and lettermarks: `references/patterns/monogram-and-lettermark.md`
- Wordmarks and lockups: `references/patterns/wordmark-and-lockup.md`
- Badges and emblems: `references/patterns/badge-and-emblem.md`
- Line drawing, stroke trace, and draw order: `references/patterns/line-drawing-and-trace.md`
- Separation, explode, and occlusion order: `references/patterns/separation-and-explode.md`
- Per-glyph and variable-axis typography: `references/patterns/kinetic-typography.md`
- Idle loops, rest states, and interactive sets: `references/patterns/idle-and-ambient.md`
- Particles, dissolve, turbulence, and glitch: `references/patterns/matter-and-particles.md`
- Education/LMS context: `references/contexts/education-and-lms.md`
- Premium/minimal context: `references/contexts/premium-and-minimal.md`
- Playful/character context: `references/contexts/playful-and-character.md`
- Technology/software context: `references/contexts/technology-and-software.md`
- Wellness/organic context: `references/contexts/wellness-and-organic.md`
- Backgrounds, alpha, codecs, and formats: `references/delivery/backgrounds-and-formats.md`, `references/delivery/alpha-and-codecs.md`
- Accessibility and reduced motion: `references/delivery/accessibility-and-reduced-motion.md`
- Remotion implementation: `references/implementation/remotion.md`
- Flattened-raster implementation: `references/implementation/flattened-raster.md`
- SVG/Lottie implementation: `references/implementation/vector-and-lottie.md`
- Cross-renderer mechanics for the advanced families: `references/implementation/advanced-mechanics.md`
- After Effects implementation: `references/implementation/after-effects.md`
- Manifest contract: `references/qa/motion-manifest.md`, `schemas/motion-spec.schema.json`
- QA gates: `references/qa/qa-checklist.md`
- Review matrix: `references/qa/review-matrix.md`
- Failure catalog: `references/qa/failure-catalog.md`
- Research provenance: `references/sources.md` (read when validating principles or updating the skill)

## Useful bundled utilities

Run commands from the skill root or use absolute paths. Python utilities require Python 3.10+; optional packages are listed in `requirements.txt`.

- `python scripts/inspect_logo_assets.py path/to/logo.png` reports dimensions, alpha bounds, and large connected components; it does not extract semantic layers.
- `python scripts/validate_motion_spec.py path/to/motion-spec.json` validates the manifest contract.
- `python scripts/make_checkpoint_contact_sheet.py --input video.mp4 --output contact-sheet.jpg --frames 0,30,60,96,119` creates a frame-accurate review sheet.
- `python scripts/compare_final_frame.py --reference reference.png --encoded video.mp4 --frame 119 --tolerance 0.03` performs a documented final-state check; add `--allow-opaque` only when an opaque white/brand render is intentionally being compared to a transparent reference.
- `python scripts/profile_logo.py path/to/logo.svg` reports the structural fingerprint, capability rung, ranked techniques, and gated techniques with their codes; add `--draw-plan` for the stroke draw-on ordering and `--json` for machine-readable output.
- `python scripts/profile_logo.py --self-test` is a dependency-free smoke test of the profiler; it needs no Pillow, NumPy, or SciPy.
- `python scripts/check_skill.py` is a dependency-free self-check of this package (frontmatter, reference links, schema, eval fixtures, the manifest validator, the advanced manifest channels, and the profiler); run it after editing the skill.

## Output contract

For `produce` mode, return or save:

- A concept summary with the primary motion idea and brand-fit reason.
- A motion brief and manifest with source capability, timing, layers, pivots, easing, outputs, and final-state acceptance criteria.
- The structural profile and ranked recommendation, with any gate codes, any override reason, and the confidence value used.
- Editable source when semantically available, or a documented reconstruction request/fallback when it is not.
- A master animation and requested background/codec variants.
- A static poster/end frame.
- Exact checkpoint contact sheet, stream metadata, and final-state comparison notes.
- Direct transition stills for raster opacity crossfades, plus decoded transition-frame evidence when a crossfade is used.
- Known limitations, inferred decisions, licensing notes, and reproduction commands.

For `plan` or `audit` mode, stop before rendering and return only the requested plan/report. For `interactive` mode, include state definitions, triggers, focus/keyboard behavior, and a static/reduced branch.
