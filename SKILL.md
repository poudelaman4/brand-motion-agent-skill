---
name: animation-logo-skill
description: Create, storyboard, render, or QA motion for an approved logo, monogram, lettermark, wordmark, emblem, or brand mark while preserving canonical geometry and the final lockup. Use for logo reveals, intros, stingers, loops, interactive states, motion briefs/manifests, and SVG, Lottie/dotLottie, Remotion, transparent/white/dark video, poster delivery, or QA. Trigger on requests to animate a logo/mark or review an existing logo animation; do not use for static logo redesign, font/glyph extraction, generic motion graphics, product animation, or format-only video conversion.
compatibility: Designed for filesystem-enabled agents. Optional Python, Pillow, NumPy, SciPy, FFmpeg, and a renderer such as Remotion may be used when available; unavailable renderers stop at the renderer-neutral brief/manifest and mark rendering blocked.
metadata:
  version: "1.2"
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

## Workflow

1. **Intake:** identify the canonical source, task mode, and whether independent layer motion is mandatory. Treat other missing preferences as documented provisional defaults.
2. **Classify:** record anatomy, narrative archetype, context, mode, runtime, background, and platform. Read `references/taxonomy.md`.
3. **Lock the source:** identify approved variants, layer inventory, alpha mode, profile, resolution, and pivots. Run the inspector on raster sources.
4. **Choose a concept:** select one primary pattern from the matching reference. Keep the wordmark subordinate until the mark is readable unless text is the hero.
5. **Write the brief:** fill `assets/motion-brief-template.json`; keep the executable manifest in `assets/motion-manifest-template.json`.
6. **Storyboard:** define the opening state, two to four milestones, settle frame, final hold, reduced-motion state, and acceptance checks before coding.
7. **Build:** use approved source geometry. Extract or request layers once, store tight crops with bounds, and animate transforms/opacity around semantic pivots. Do not segment per frame. For any extracted raster crossfade, inspect the layer alone and render the exact transition midpoint before accepting it.
8. **Render variants:** derive outputs from the canonical spec using separate compositions or state definitions as needed.
9. **QA:** render exact checkpoint frames, inspect the decoded video, compare the final state to the reference, and test target players/backgrounds. For opacity crossfades, inspect direct start/mid/end stills and decode the same frames from the final file. Read `references/qa/qa-checklist.md`.
10. **Package:** deliver the source, final motion, static poster, required variants, manifest, render commands, and a pass/warn/blocked report.

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
- Pattern feasibility by source type: `references/patterns/feasibility.md`
- Intake, defaults, and approvals: `references/intake-and-planning.md`
- Timing, easing, pivots, and layer grammar: `references/motion-foundations.md`
- Organic/botanical marks: `references/patterns/organic-botanical.md`
- Geometric/constructive marks: `references/patterns/geometric-constructive.md`
- Monograms and lettermarks: `references/patterns/monogram-and-lettermark.md`
- Wordmarks and lockups: `references/patterns/wordmark-and-lockup.md`
- Badges and emblems: `references/patterns/badge-and-emblem.md`
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

## Output contract

For `produce` mode, return or save:

- A concept summary with the primary motion idea and brand-fit reason.
- A motion brief and manifest with source capability, timing, layers, pivots, easing, outputs, and final-state acceptance criteria.
- Editable source when semantically available, or a documented reconstruction request/fallback when it is not.
- A master animation and requested background/codec variants.
- A static poster/end frame.
- Exact checkpoint contact sheet, stream metadata, and final-state comparison notes.
- Direct transition stills for raster opacity crossfades, plus decoded transition-frame evidence when a crossfade is used.
- Known limitations, inferred decisions, licensing notes, and reproduction commands.

For `plan` or `audit` mode, stop before rendering and return only the requested plan/report. For `interactive` mode, include state definitions, triggers, focus/keyboard behavior, and a static/reduced branch.
