# Vector and Lottie Implementation

## Contents

- SVG
- Lottie and dotLottie
- Morphs
- Theme and state
- Export preflight
- QA

## SVG

Prefer transforms and opacity for simple reveals. Use `pathLength` or stroke-dash techniques for deliberate line drawing. Preserve viewBox, group names, masks, and exact path data. Test `transform-box`, clipping, browser support, and external-resource restrictions.

Before shipping, check:

- live text versus outlined glyphs
- RTL, vertical, and non-Latin metrics
- masks, clipping paths, gradients, filters, and blend modes
- stroke expansion and `pathLength` behavior
- scripts, `foreignObject`, external URLs, and remote assets
- whether the target runtime allows animation at all

## Lottie and dotLottie

Use a timeline for a one-shot intro or loop. Use a state machine for hover, press, active, selected, or reactive behavior. dotLottie can preserve richer state behavior where the target runtime supports it; pin the package version and test the actual player.

Validate shape-layer order, transforms, path structure, trim paths, expressions, masks, fonts, themes, and state-machine assets. Do not assume an authoring tool's preview matches the runtime.

## Morphs

Morph only between compatible paths with matching open/closed state, vertex count/order, and tangent structure. If compatibility is uncertain, use a mask, crossfade, or assembly instead. Never morph an approved wordmark into an unapproved glyph shape.

## Theme and state

Keep brand-color changes in theme variables or controlled state layers. Do not make state meaningful only through color or motion. Provide a static fallback for unsupported runtimes and a host-selected reduced-motion asset.

## Export preflight

- Outline or embed fonts.
- Remove unsupported scripts/external references or document their runtime requirement.
- Flatten or explicitly approve masks, gradients, filters, and blend modes.
- Check text-on-path orientation and RTL behavior.
- Validate path order before any morph.
- Confirm the output includes no authoring grid, hidden layer, or unresolved expression.

## QA

- Validate the asset in the target player, not only in an authoring tool.
- Check first/last loop states, frame rate, asset loading, and state transitions.
- Inspect at small sizes and on light/dark/brand backgrounds.
- Confirm text, masks, blend modes, and alpha survive export.
- Provide source vectors and a poster frame alongside the runtime asset.
