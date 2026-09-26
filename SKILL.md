---
name: animation-logo-skill
description: Detect the structure of an approved logo or mark, rank the motion techniques that structure supports, filter them through the brand register, then create, storyboard, render, or QA the motion while preserving canonical geometry and the final lockup. Covers basic reveals plus line drawing, separation, kinetic typography, morph, gradient sweeps, particles, and idle loops, with the craft that applies to all of them: light and shadow, depth and material, camera, and pace. Adds taste judgement, cliche and restraint doctrine, and the real delivery contexts from broadcast and product UI to social, signage, and live events. Trigger on requests to animate a logo or mark, to decide which animation a logo can or should have, or to review an existing logo animation; do not use for static logo redesign, font or glyph extraction, generic motion graphics, product animation, or format-only video conversion.
compatibility: Designed for filesystem-enabled agents. Optional Python, Pillow, NumPy, SciPy, FFmpeg, and a renderer such as Remotion may be used when available; unavailable renderers stop at the renderer-neutral brief/manifest and mark rendering blocked.
metadata:
  version: "1.4"
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
- Confirm the deliverable and how often one person will see it before choosing anything. Frequency is the strongest restraint mechanism there is: the same mark seen daily and once a year justify two entirely different amounts of motion.
- Never ship a recommendation that has not passed the taste gate. The gate is not optional and the manifest validator rejects a detection block with no register and no taste budget, so an ungated recommendation cannot reach delivery.
- Resolve taste before craft. A register veto removes a technique outright; do not demote a vetoed technique and do not spend craft budget on a move the brand has declined.
- Name the referent for every movement: physical, structural, historical, or semiotic. A movement with no referent is decoration and must survive the delete test.
- Honour the platform before the preference. A platform guideline, a legal minimum, and a stated brand claim all outrank an inferred register or a structural opportunity.
- Treat light and shadow as claims about volume, not as polish. A shadow is a relationship between two surfaces, so a shadow on a transparent master with no catcher is a defect.
- Probe the environment before promising a deliverable, and never install anything without the user's agreement. Print the command and let the user run it.
- Never promise a renderer rung the machine cannot support, and never fall to a lower rung without agreeing it with the user first. A substitution that changes what the motion looks like must be recorded, not absorbed.
- Treat generative video as a plate source, never an identity source. A model may produce atmosphere, texture, b-roll, and background; it may not produce the mark, the wordmark, or the lockup. Record the model, version, prompt, and seed, because a plate with no seed is not a deliverable.
- Keep the camera, artboard, clear space, and final lockup stable. Animate inside a fixed composition rather than repeatedly reframing the logo.
- Treat the final state as a golden state. Verify canonical geometry, text metrics, color, alpha, and clear space against the reference; use documented tolerances for encoded RGB output.
- For Remotion or other rendered video, drive every value from the frame number. Explicit state machines are allowed for interactive SVG/dotLottie runtimes.
- Never silently fabricate hidden detail when a flattened source does not contain separable layers. Offer a grouped or whole-mark fallback and state the limitation.
- Treat raster layers extracted from a flattened source as provisional reconstruction assets. A clean-looking layer can still carry low-alpha ringing or crop contamination that becomes visible during an opacity crossfade; prefer approved vector geometry for continuous rings and contours.
- One canonical motion specification and timing model may feed separate square, vertical, horizontal, alpha, white, dark, and interactive compositions. Do not regenerate each variant from scratch.

## Source capability gate

Determine whether the source is vector, layered, or a flattened composite before promising any independent motion. A flattened raster defaults to a whole-mark reveal, a grouped mask, or an approved group list; independent letters, leaves, and hidden overlaps are `BLOCKED` until the user approves a reconstruction. Live text must be outlined or embedded, never left to a runtime font.

Connected components are evidence, not layers. `references/patterns/feasibility.md` states what each family requires per source type, and `profile_logo.py` reports the source's capability rung and a gate code for every technique it rules out. Read the feasibility table before choosing, and the gate codes in the profiler output rather than judging capability by eye.

## Workflow

1. **Intake:** identify the canonical source, task mode, and whether independent layer motion is mandatory. Treat other missing preferences as documented provisional defaults.
2. **Probe the environment:** run `python scripts/check_environment.py` before promising a render, checkpoint sheet, or final-state check. Treat `degraded` as a documented loss, `missing` as a choice to offer the user rather than an install to perform, and `blocked` as a delivery-scope change to agree before falling to a lower renderer rung. Read `references/setup-and-environment.md`.
3. **Classify:** record anatomy, narrative archetype, context, mode, runtime, background, and platform. Read `references/taxonomy.md`.
4. **Lock the source:** identify approved variants, layer inventory, alpha mode, profile, resolution, and pivots. Run the inspector on raster sources.
5. **Profile and recommend:** run `scripts/profile_logo.py` on the locked source. Read the capability rung, the ranked techniques, the gated techniques and their codes, and the draw plan when line drawing is in contention. Keep at most one primary and two supporting; the brand context modifier still decides. Read `references/technique-selection.md`.
6. **Apply taste and context:** run the profiler with `--register` and `--frequency`. The register is required and the profiler refuses to run without it, because taste is a judgement about the brand and not a property of the file. Take the register from a stated brand claim or an explicit user answer and label the inference `inferred`; never infer it from the asset's structure. Drop every vetoed technique rather than demoting it, note the register as the reason, read the cliche warnings, and take the duration, gesture, and overshoot ceilings from the taste block. Read `references/taste/brand-register.md`, `references/taste/cliche-and-restraint.md`, and `references/taste/fit-decisions.md`.
7. **Choose a concept:** select one primary pattern from the matching reference. Keep the wordmark subordinate until the mark is readable unless text is the hero. When the profile or the register recommends something else, record why.
8. **Write the brief:** fill `assets/motion-brief-template.json`; keep the executable manifest in `assets/motion-manifest-template.json`.
9. **Storyboard:** define the opening state, two to four milestones, settle frame, final hold, reduced-motion state, and acceptance checks before coding. For a stroke reveal, derive the draw order from the endpoint graph and the Eulerian check rather than inventing it. Hold the wordmark at full contrast for at least the reading floor in `references/craft/pace-and-rhythm.md`.
10. **Build:** use approved source geometry. Extract or request layers once, store tight crops with bounds, and animate transforms/opacity around semantic pivots. Do not segment per frame. Carry each technique in its own channel: dash arithmetic for a draw-on, a direction and depth for a separation, matched path pairs for a morph, a mask type and angle for a wipe. For any extracted raster crossfade, inspect the layer alone and render the exact transition midpoint before accepting it.
11. **Render variants:** derive outputs from the canonical spec using separate compositions or state definitions as needed.
12. **QA:** render exact checkpoint frames, inspect the decoded video, compare the final state to the reference, and test target players/backgrounds. For opacity crossfades, inspect direct start/mid/end stills and decode the same frames from the final file. Read `references/qa/qa-checklist.md` and `references/utilities.md` for the checkpoint-sheet and final-frame commands.
13. **Revise:** on reviewer feedback, restate it as a named symptom before changing any value, change one lever, and re-render the same checkpoints. A comment that needs a canonical invariant, the register, the source, or the delivery context to move is a new brief rather than a revision, and an impossible request is reported as a conflict rather than satisfied by widening a ceiling. Read `references/taste/revision-and-feedback.md`.
14. **Package:** deliver the source, final motion, static poster, required variants, manifest, render commands, and a pass/warn/blocked report.

## Hard blockers and provisional defaults

Only three items are hard blockers:

1. No canonical source/reference, or no way to identify the approved logo.
2. The task mode is unclear enough that producing assets could be surprising.
3. Independent layer motion is mandatory but the source cannot support it and no reconstruction is approved.

Everything else can use the defaults in `assets/motion-tokens.json` and `references/intake-and-planning.md`. Record inferred values in the brief rather than silently treating them as approvals.

## Default contract

Keep an alpha master and provide a white or brand-colour fallback when the target player is uncertain. Stay silent by default and add only user-approved audio cues. Show the approved final state immediately under reduced motion, optionally with a short opacity dissolve.

Every remaining default lives in `assets/motion-tokens.json` as a value, including durations, easing curves, stagger windows, overshoot ceilings, the register budgets, the reading floor, and the lighting ranges. Read that file rather than restating a number, and change the token rather than the prose when a default moves.

## Pattern routing

Read only the references the current task needs.

Start here:

- Worked example, one logo through every step: `references/worked-example.md`
- Classification and selection: `references/taxonomy.md`
- Detection and recommendation: `references/technique-selection.md`
- Feasibility by source type: `references/patterns/feasibility.md`
- Intake, defaults, approvals: `references/intake-and-planning.md`
- Timing, easing, pivots, layers: `references/motion-foundations.md`

By anatomy:

- Organic and botanical: `references/patterns/organic-botanical.md`
- Geometric and constructive: `references/patterns/geometric-constructive.md`
- Monogram and lettermark: `references/patterns/monogram-and-lettermark.md`
- Wordmark and lockup: `references/patterns/wordmark-and-lockup.md`
- Badge and emblem: `references/patterns/badge-and-emblem.md`
- Line drawing and draw order: `references/patterns/line-drawing-and-trace.md`
- Separation and occlusion order: `references/patterns/separation-and-explode.md`
- Kinetic typography: `references/patterns/kinetic-typography.md`
- Idle and ambient: `references/patterns/idle-and-ambient.md`
- Matter and particles: `references/patterns/matter-and-particles.md`

Craft, for any technique rather than one:

- Light, shadow, elevation: `references/craft/light-and-shadow.md`
- Depth, material, surface: `references/craft/depth-and-material.md`
- Camera, perspective, framing: `references/craft/camera-and-perspective.md`
- Pace, rhythm, reading floor: `references/craft/pace-and-rhythm.md`

Taste, before choosing or reviewing:

- Register and its vetoes: `references/taste/brand-register.md`
- Cliché, machine defaults, restraint: `references/taste/cliche-and-restraint.md`
- Quality tests, review vocabulary: `references/taste/quality-tests.md`
- Fit decisions, precedence, refusals: `references/taste/fit-decisions.md`
- Revision, feedback, and what a revision may not touch: `references/taste/revision-and-feedback.md`

By context:

- Education and LMS: `references/contexts/education-and-lms.md`
- Premium and minimal: `references/contexts/premium-and-minimal.md`
- Playful and character: `references/contexts/playful-and-character.md`
- Technology and software: `references/contexts/technology-and-software.md`
- Wellness and organic: `references/contexts/wellness-and-organic.md`

Delivery:

- Backgrounds, alpha, codecs, formats: `references/delivery/backgrounds-and-formats.md`, `references/delivery/alpha-and-codecs.md`
- Broadcast, safe areas, legal minimums: `references/delivery/broadcast-and-media.md`
- Product UI and platform prohibitions: `references/delivery/digital-product-and-ui.md`
- Social and platform covered zones: `references/delivery/social-and-editorial.md`
- Signage, events, realtime: `references/delivery/physical-and-events.md`
- Motion systems and handoff: `references/delivery/motion-system-and-handoff.md`
- Accessibility and reduced motion: `references/delivery/accessibility-and-reduced-motion.md`

Implementation:

- Remotion: `references/implementation/remotion.md`
- Flattened raster: `references/implementation/flattened-raster.md`
- SVG and Lottie: `references/implementation/vector-and-lottie.md`
- Cross-renderer advanced mechanics: `references/implementation/advanced-mechanics.md`
- After Effects: `references/implementation/after-effects.md`

QA and provenance:

- Environment, renderer ladder, and install guidance: `references/setup-and-environment.md`
- Generative video as a constrained plate source: `references/delivery/generative-and-ai-video.md`
- Manifest contract: `references/qa/motion-manifest.md`
- QA gates: `references/qa/qa-checklist.md`
- Review matrix: `references/qa/review-matrix.md`
- Failure catalog: `references/qa/failure-catalog.md`
- Research provenance: `references/sources.md`

## Useful bundled utilities

Three utilities matter in every mode:

- `python scripts/profile_logo.py path/to/logo.svg --register <register>` measures the source, ranks techniques, applies the register veto, and returns the taste budget. `--register` is required. Read `references/utilities.md` for every flag, the remaining scripts, and what each one does not do.

Run `python scripts/check_environment.py` to see what this machine can do, and `python scripts/check_skill.py` after editing this package.

## Output contract

For `produce` mode, return or save:

- A concept summary with the primary motion idea and brand-fit reason.
- A motion brief and manifest with source capability, timing, layers, pivots, easing, outputs, and final-state acceptance criteria.
- The structural profile and ranked recommendation, with any gate codes, any override reason, and the confidence value used.
- The register, the frequency assumption, the taste budget, every vetoed technique with its reason, and any cliche warning that was accepted.
- Editable source when semantically available, or a documented reconstruction request/fallback when it is not.
- A master animation and requested background/codec variants.
- A static poster/end frame.
- Exact checkpoint contact sheet, stream metadata, and final-state comparison notes.
- Direct transition stills for raster opacity crossfades, plus decoded transition-frame evidence when a crossfade is used.
- Known limitations, inferred decisions, licensing notes, and reproduction commands.

For `plan` or `audit` mode, stop before rendering and return only the requested plan/report. For `interactive` mode, include state definitions, triggers, focus/keyboard behavior, and a static/reduced branch.
