# Logo Animation QA Checklist

## Contents

- Contract
- Source and layers
- Visual motion
- Typography
- Performance
- Delivery
- Accessibility
- Handoff

## Contract

- [ ] Task mode is explicit: audit, plan/storyboard, produce, or interactive.
- [ ] Approved static master and permitted variants are identified.
- [ ] Target dimensions, aspect ratio(s), fps, frame count, duration, codec, and player/editor are explicit.
- [ ] Four-second timing is recorded as 120 frames at 30 fps, or the actual equivalent.
- [ ] Primary motion concept and supporting gestures are named.
- [ ] Final hold, settle frame, and poster frame are defined.
- [ ] Source capability is recorded: vector, layered raster, flattened raster, or live text.

## Source and layers

- [ ] Source limitation is stated and independent-motion requirements are marked observed/provisional/blocked.
- [ ] Confirm the recorded structural profile was taken from the locked source file, not a draft, alternate, or superseded variant; re-profile whenever the source checksum changes.
- [ ] Record a written reason for every recommendation overridden from the profiler's ranking, and name the structural feature that carried the surviving technique.
- [ ] List every gated technique under `blocked` with its gate code, detail, and remedy, per `references/technique-selection.md`; clear no gate silently and let no blocked technique reach the plan.
- [ ] Every layer has valid alpha and a source file when semantically available.
- [ ] Bounds, z-order, pivot, confidence, and final-state status are recorded.
- [ ] Pivots use semantic anchors, not arbitrary box centers.
- [ ] Crops are inspected over white, black, checkerboard, and a saturated color.
- [ ] No accidental matte, halo, hidden background, doubled shadow, or missing overlap is visible.
- [ ] Extracted raster layers are treated as provisional reconstruction assets; residual pixels, low-alpha components, and crop contamination are checked before motion.
- [ ] Label component counts, hole counts, and symmetry scores derived from a flattened raster `provisional`, and keep them out of the `observed` column.
- [ ] Every opacity crossfade between two representations has direct start/mid/end stills; rings and continuous outlines are checked for ghost contours.
- [ ] Tight crops are used for high-resolution transparent layers.
- [ ] Flattened-source reconstructions, if any, have fresh approval.

## Visual motion

- [ ] Exact frame 0, early checkpoint, midpoint, late checkpoint, settle, poster, and pre-settle frames are inspected.
- [ ] No collisions, clipping, tangencies, or late micro-adjustments occur.
- [ ] Overshoot stays within the selected pattern limits.
- [ ] Final state is fully settled and has no blur, glow, guide, or temporary scaffolding.
- [ ] Transition frames are reviewed at 100% and thumbnail size; no pale duplicate contours, halos, or matte fragments appear during partial opacity.
- [ ] The logo is recognizable at thumbnail size.
- [ ] The wordmark does not compete with the primary mark unless intended.
- [ ] Parallel timing feels intentional rather than queued.
- [ ] Alternate aspect ratios have their own clear-space and clipping checks.
- [ ] Confirm every stroke layer's dash array is at least its measured path length; a shorter array re-dashes the path mid-draw.
- [ ] Record a stroke order, a start-point rule, and a declared pen-lift count for a multi-stroke draw, and match the pen-lift count to the source's odd-degree vertex count, per `references/patterns/line-drawing-and-trace.md`.
- [ ] Inspect occlusion order at the separation midpoint as well as at the endpoints; a front part passing behind a back layer reads as a pass-through.
- [ ] Compare the return leg of a separate-and-return beat against the outbound leg with easing inverted and no re-timing, per `references/patterns/separation-and-explode.md`; any other pairing pops at the turnaround.
- [ ] Inspect the mask or wipe edge where it crosses a counter mid-transition, and confirm no counter is shaved at that frame.
- [ ] Record the mask feather value with its unit wherever a mask reports one; an implicit feather renders differently per player.

## Typography

- [ ] Approved font/outlines are used.
- [ ] Kerning, counters, baseline, language direction, and descriptor spacing match the master.
- [ ] Measure the settled tracking and sidebearings against the approved wordmark and record the delta; never renormalize tracking after the fact.
- [ ] Re-verify a variable-axis reveal at both axis extremes, weight and width, and confirm every animated axis returns to its approved value at the settle frame, per `references/patterns/kinetic-typography.md`.
- [ ] No glyph substitution, reflow, broken join, or partial clipping occurs.
- [ ] Letter-by-letter motion is optically checked if used.
- [ ] Re-measure a per-glyph reveal after the face resolves and rebake the advances; numbers taken before the face loads stay `provisional`.
- [ ] Text-on-path, RTL, vertical, and non-Latin cases are explicitly handled.

## Performance

- [ ] Confirm every animated value is a pure function of the frame number and props; mark runtime randomness, wall-clock time, timers, unthrottled animation-frame driving, and module-scope counters `blocked` in a frame-driven renderer.
- [ ] Render the same frame range twice and diff the output; any difference between runs is a defect, not noise.
- [ ] Check per-part blur, particle count, and animated area against the stated budgets, and record the measured values: near 12 blurred parts, 60-120 particles for a one-shot reveal, and at most 0.5% of the frame budget for a header mark, per `references/patterns/matter-and-particles.md`.

## Delivery

- [ ] Master and requested variants are encoded.
- [ ] Stream metadata is checked for frame count, fps, duration, codec, pixel format, color range/profile, and alpha mode.
- [ ] Decoded checkpoint and poster frames are inspected.
- [ ] Exact crossfade transition frames are decoded from the final encoded file, not only rendered as composition stills.
- [ ] Target player/editor plays the file without load flicker or missing assets.
- [ ] Alpha, white, dark, and opaque variants are separate and intentional.
- [ ] Poster/end frame and reduced-motion asset are supplied.
- [ ] Render command, dependencies, and source version are recorded.
- [ ] Color-managed comparison uses a documented encoded-output tolerance.

## Accessibility

- [ ] Reduced-motion version shows the approved final state.
- [ ] Supply a reduced-motion branch for every technique family in the plan, not for the base reveal alone: draw-on, separation, morph, mask, effects, and idle.
- [ ] The host selects the reduced/static asset; CSS media queries alone are not assumed to stop arbitrary video/Lottie playback.
- [ ] Automatic motion has a static alternative or skip path where applicable.
- [ ] Interactive state has keyboard, focus, and non-motion equivalents.
- [ ] No rapid flashing or sound-dependent essential information exists.
- [ ] Motion controls are documented for long or repeating sequences.
- [ ] Confirm an idle loop is pausable from the keyboard and that its rest state is the approved final frame, held with no dissolve longer than 150 ms, per `references/patterns/idle-and-ambient.md`.
- [ ] Decorative marks are hidden from assistive technology; informative marks have an appropriate text alternative.

## Handoff

- [ ] Editable source is included when semantically available.
- [ ] Motion brief and manifest are included.
- [ ] Record every channel the plan uses in its own manifest block, rather than overloading the transform channel: draw-on as `stroke`, part motion as `separation`, path interpolation as `morph`, and clipping, effects, and detection each in their own field.
- [ ] Contact sheet, decoded poster, stream metadata, and comparison JSON are included.
- [ ] Licensing, font, and third-party asset notes are included.
- [ ] Known limitations and provisional decisions are clearly labeled.
- [ ] Step a morph through its intermediate frames, not only its endpoints, and reject any self-intersection or any counter that opens or closes mid-transition, per `references/implementation/advanced-mechanics.md`.
