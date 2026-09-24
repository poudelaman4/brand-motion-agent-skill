# Backgrounds and Formats

## Contents

- Background treatments
- Format matrix
- White and alpha separation
- Aspect ratios
- Handoff checklist

## Background treatments

### Alpha master

Use for compositing and editorial workflows. Keep the background transparent and inspect the logo over checkerboard, white, black, and photography. Confirm whether the asset uses straight or premultiplied alpha.

### Pure white matte

Use when the user requests a white-background animation. Render the same timing model over exact `#FFFFFF`; do not bake this matte into the alpha master.

### Brand or dark background

Use separate compositions or an explicit background prop from the canonical timing model. Do not recolor the canonical logo without approval.

## Format matrix

| Use | Preferred output | Notes |
|---|---|---|
| Editable handoff | Layered SVG/PDF and project source | Preserve paths, masks, groups, and kerning |
| Responsive web | Animated SVG | Test target browsers, text, masks, and reduced motion |
| App/modern web | dotLottie | Verify version, assets, themes, and state-machine support |
| Legacy web | Lottie JSON | Verify runtime feature support and expression limits |
| Editorial master | PNG sequence or ProRes 4444/XQ | Preserve alpha semantics and color management |
| Transparent web | WebM VP8/VP9 with alpha | Test browser/player support, banding, and chunk boundaries |
| General video | H.264 MP4 | Reliable opaque fallback; do not call it transparent |
| Static fallback | SVG plus high-resolution PNG | Required for poster, print, and reduced motion |

## White and alpha separation

Treat these as separate compositions or explicit background props. A white-background video is opaque even when source PNGs have alpha. A transparent master must not contain a hidden white matte, a shadow baked into the logo, or a black background.

## Aspect ratios

Do not stretch the logo. Use a normalized source artboard and define layout rules per ratio. Recompose square, vertical, and horizontal versions independently, then check clear space and clipping at the largest animated scale. Multiple outputs may share a canonical timing model but require separate canvas and clear-space acceptance checks.

## Handoff checklist

- Editable source when semantically available
- Master animation and requested variants
- Static poster/end frame
- Alpha, white, dark, and opaque variants when relevant
- Reduced-motion version
- Motion brief and manifest
- Render command and dependency notes
- Licensing and font information
- QA contact sheet and encoded-output metadata
