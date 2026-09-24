# Logo Animation QA Checklist

## Contents

- Contract
- Source and layers
- Visual motion
- Typography
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
- [ ] Every layer has valid alpha and a source file when semantically available.
- [ ] Bounds, z-order, pivot, confidence, and final-state status are recorded.
- [ ] Pivots use semantic anchors, not arbitrary box centers.
- [ ] Crops are inspected over white, black, checkerboard, and a saturated color.
- [ ] No accidental matte, halo, hidden background, doubled shadow, or missing overlap is visible.
- [ ] Tight crops are used for high-resolution transparent layers.
- [ ] Flattened-source reconstructions, if any, have fresh approval.

## Visual motion

- [ ] Exact frame 0, early checkpoint, midpoint, late checkpoint, settle, poster, and pre-settle frames are inspected.
- [ ] No collisions, clipping, tangencies, or late micro-adjustments occur.
- [ ] Overshoot stays within the selected pattern limits.
- [ ] Final state is fully settled and has no blur, glow, guide, or temporary scaffolding.
- [ ] The logo is recognizable at thumbnail size.
- [ ] The wordmark does not compete with the primary mark unless intended.
- [ ] Parallel timing feels intentional rather than queued.
- [ ] Alternate aspect ratios have their own clear-space and clipping checks.

## Typography

- [ ] Approved font/outlines are used.
- [ ] Kerning, counters, baseline, language direction, and descriptor spacing match the master.
- [ ] No glyph substitution, reflow, broken join, or partial clipping occurs.
- [ ] Letter-by-letter motion is optically checked if used.
- [ ] Text-on-path, RTL, vertical, and non-Latin cases are explicitly handled.

## Delivery

- [ ] Master and requested variants are encoded.
- [ ] Stream metadata is checked for frame count, fps, duration, codec, pixel format, color range/profile, and alpha mode.
- [ ] Decoded checkpoint and poster frames are inspected.
- [ ] Target player/editor plays the file without load flicker or missing assets.
- [ ] Alpha, white, dark, and opaque variants are separate and intentional.
- [ ] Poster/end frame and reduced-motion asset are supplied.
- [ ] Render command, dependencies, and source version are recorded.
- [ ] Color-managed comparison uses a documented encoded-output tolerance.

## Accessibility

- [ ] Reduced-motion version shows the approved final state.
- [ ] The host selects the reduced/static asset; CSS media queries alone are not assumed to stop arbitrary video/Lottie playback.
- [ ] Automatic motion has a static alternative or skip path where applicable.
- [ ] Interactive state has keyboard, focus, and non-motion equivalents.
- [ ] No rapid flashing or sound-dependent essential information exists.
- [ ] Motion controls are documented for long or repeating sequences.
- [ ] Decorative marks are hidden from assistive technology; informative marks have an appropriate text alternative.

## Handoff

- [ ] Editable source is included when semantically available.
- [ ] Motion brief and manifest are included.
- [ ] Contact sheet, decoded poster, stream metadata, and comparison JSON are included.
- [ ] Licensing, font, and third-party asset notes are included.
- [ ] Known limitations and provisional decisions are clearly labeled.
