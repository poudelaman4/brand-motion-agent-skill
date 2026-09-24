# Flattened Raster Logos

## Contents

- Capability decision
- Safe inspection
- Grouping and reconstruction
- Alpha and resolution
- Fallback patterns
- Approval requirements

## Capability decision

A flattened PNG/SVG is an approved final image, not an approved layer inventory. It may be suitable for a whole-mark mask, grouped fade, silhouette reveal, or approved manually masked groups. It is not sufficient for reliable independent letters, leaves, hidden overlaps, or text-on-path motion.

Before promising independent animation, record:

- image dimensions, effective resolution, DPI, ICC profile, and alpha mode
- visible bounding box and transparent corners
- whether the source is straight or premultiplied alpha
- whether the raster is a screenshot, export, or camera-derived image
- known occlusions and overlaps
- whether the user approves a separately reconstructed vector/raster asset

## Safe inspection

`python scripts/inspect_logo_assets.py logo.png` reports alpha bounds and connected components. Connected components can be split by antialiasing, shadows, gradients, or touching pixels; they are evidence for manual review, not semantic layers.

Inspect each candidate layer alone and in the complete composite. A layer extracted from a composite may contain blended edge pixels or no hidden detail behind an overlap.

## Grouping and reconstruction

Prefer, in order:

1. Original vector/layered source from the brand owner
2. Manually approved groups made from the original artwork
3. Whole-mark mask or grouped fade that does not reveal hidden pixels
4. A separately created redraw/vectorization, approved as a new source asset

Do not call OCR, segmentation, or automatic vectorization an identity truth. Any reconstructed asset needs a new approval checkpoint.

## Alpha and resolution

- Check for hidden white or black mattes.
- Inspect edges on white, black, checkerboard, and saturated backgrounds.
- Use clean straight/premultiplied-alpha semantics consistently.
- Do not promise large high-resolution output from a low-resolution raster; report effective DPI and recommend a vector or higher-resolution source.
- Keep tight crops and explicit bounds for any approved raster layers.

## Fallback patterns

- Whole-mark opacity/translate reveal
- Directional mask reveal
- Grouped leaf/ring/wordmark regions where the user approves the grouping
- Silhouette-to-color fill if the source has a usable silhouette and approved colors
- Static end frame with a short dissolve when independent motion is blocked

## Approval requirements

Before reconstruction or aggressive masking, obtain approval for:

- layer grouping and z-order
- pivot locations
- hidden/occluded areas
- crop boundaries
- any redrawn letters, counters, veins, or colors
- final-state reference and acceptance tolerance
