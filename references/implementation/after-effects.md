# After Effects Implementation

## Contents

- Composition setup
- Layer strategy
- Timing and expressions
- Masks and effects
- Render and QA

## Composition setup

Use a fixed composition duration, frame rate, artboard, and background. Interpret the motion manifest as the source of timing; use shape layers, mattes, masks, and approved vector artwork where available.

## Layer strategy

Keep semantic layers named and ordered. Use tight raster crops for approved raster groups, preserve source bounds, and set anchor points at the manifest pivots. Avoid animating layout dimensions or rebuilding the logo from a flattened image at runtime.

## Timing and expressions

Prefer explicit keyframes for the canonical timeline. Expressions may calculate simple values from time or layer properties, but the final hold must be deterministic. Avoid uncontrolled randomness and do not use a spring-like expression that has not settled by the poster frame.

## Masks and effects

Use masks, track mattes, trim paths, and shape layers for trace, weave, and mask concepts. Keep glow, blur, grain, and generated texture outside the canonical logo unless explicitly approved. Check unsupported effects and blends in the final render.

## Render and QA

Render a poster frame, exact checkpoints, and the final frame. Test alpha and opaque backgrounds, alternate aspect ratios, motion blur, and target codecs. Confirm the final state against the approved source with documented encoded-output tolerance.
