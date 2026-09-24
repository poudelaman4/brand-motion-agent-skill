# Intake and Planning

## Contents

- Hard blockers
- Provisional defaults
- Source capability
- Concept brief
- Approval gates
- Planning pitfalls

## Hard blockers

Ask only for choices that materially change whether work can be trusted:

1. **Canonical source:** identify the approved static logo and permitted variants.
2. **Task mode:** audit, plan/storyboard, produce, or interactive.
3. **Independent-motion requirement:** state whether true independent letters/leaves/layers are mandatory or a grouped/whole-mark treatment is acceptable.

If any blocker is unresolved, produce an audit or plan with `blocked` fields rather than fabricating an implementation.

## Provisional defaults

Use these when the user is vague and record the choice as provisional:

| Decision | Default |
|---|---|
| One-shot duration | 1.2–2.4 s; up to 4 s for detailed organic/wordmark sequences |
| Frame rate | 30 fps for rendered video |
| Final hold | 500–1000 ms for an intro |
| Primary gesture | One dominant trace, assemble, unfold, or mask |
| Wordmark | Settle after the mark is readable |
| Overshoot | 0% for identity-critical geometry; at most 5% organic; at most 8% playful |
| Background | Alpha master plus white or brand fallback |
| Audio | Silent |
| Reduced motion | Immediate approved final state, optional short dissolve |
| Delivery | Source, master video, static poster, manifest, and QA report |

Numeric tokens are maintained in `assets/motion-tokens.json`; override them only with a documented reason.

## Source capability gate

Record the source type before choosing a pattern:

- `vector`: SVG/PDF/EPS/AI or approved vectorized master
- `layered-raster`: separate approved raster groups with alpha
- `flattened-raster`: one composite image
- `live-text`: editable text requiring outline/embed treatment

For each source record dimensions, effective resolution/DPI, alpha mode, color profile, masks, text outlines, known occlusions, and whether a redraw is approved.

### Vector source

Preserve original paths, groups, masks, and kerning. Use vector anchors for pivots. Compatible morphs are possible only when topology and point order are controlled.

### Layered raster source

Use each approved group as a semantic unit. Keep tight crops and a manifest with source bounds, z-order, pivot, and confidence. Inspect edges on multiple backgrounds.

### Flattened raster source

A composite can support a whole-mark reveal, mask, silhouette, or manually approved grouped animation. It cannot reveal occluded pixels or guarantee independent letter/leaf motion. Treat automatic segmentation and vectorization as provisional evidence, not identity truth. If independent motion is mandatory, request original layers or approval for a separately reconstructed asset.

### Live text

Outline or embed the approved wordmark for rendering. Preserve optical kerning, language direction, and non-Latin glyphs.

## Concept brief

Fill `assets/motion-brief-template.json` before coding. It should contain:

```text
brand_intent:
approved_source:
source_capability:
task_mode:
primary_concept:
why_it_fits:
opening_state:
milestones:
settle_frame:
hold_start_frame:
layer_inventory:
canonical_invariants:
background_variants:
reduced_motion_state:
forbidden_effects:
acceptance_checks:
approval_status:
decision_log:
```

The executable manifest is separate: `assets/motion-manifest-template.json`.

## Approval gates

1. **Concept gate:** user approves the primary idea and mood.
2. **Geometry gate:** user approves the layer inventory, pivots, and canonical reference.
3. **Timing gate:** checkpoint stills show a readable progression and a static hold.
4. **Delivery gate:** encoded files and target-player playback pass.
5. **Handoff gate:** final state, variants, commands, limitations, and licensing notes are documented.

When the user requests autonomous execution, do not stop for every inferred choice; record provisional decisions and continue only when no hard blocker remains.

## Planning pitfalls

- A four-second label is not enough; record fps and frame count.
- `useCurrentFrame()` is zero-based; the last frame is `durationInFrames - 1`.
- Use half-open layer intervals and define rounding for fractional frame rates.
- A `spring()` that overshoots must settle before the final hold.
- Do not animate a wordmark letter-by-letter when the approved font has fragile joins or the brand calls for quiet typography.
- Do not use a center pivot for a leaf when its root/base is visible.
- Do not use one full-canvas transparent image per layer at high resolution; crop layers and retain explicit bounds to reduce decode memory.
- Keep the source artboard fixed and compose alternate aspect ratios deliberately.
- Do not promise pixel-identical encoded output; compare canonical geometry and use documented tolerances for color/codec output.
