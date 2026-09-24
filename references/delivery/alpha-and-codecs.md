# Alpha and Codec Guidance

## Contents

- Alpha choices
- Common output profiles
- Validation
- Failure prevention

## Alpha choices

- **PNG sequence:** lossless transparent intermediate for editorial work; large storage.
- **ProRes 4444/4444-xq MOV:** robust editorial alpha master; alpha is mathematically lossless, while the color path still needs color management.
- **WebM VP8/VP9 with alpha:** useful for supported web playback; test browser support, banding, and chunk boundaries. Safari and other players may not support the same alpha path.
- **HEVC with alpha:** useful in some Apple/editorial pipelines; do not assume universal playback.
- **H.264 MP4:** reliable opaque fallback; do not describe it as transparent.

## Common output profiles

| Goal | Container/codec | Background |
|---|---|---|
| Social/web fallback | H.264 MP4 | White, brand, or dark matte |
| Transparent web | WebM VP8/VP9 alpha, commonly `yuva420p` | Transparent |
| Editing master | PNG sequence or ProRes 4444/XQ | Transparent |
| Vector web | SVG | Transparent or themeable |
| Modern interactive | dotLottie | Themeable/stateful |

## Validation

Inspect the encoded stream, not only the source composition. Confirm dimensions, fps, frame count, duration, codec, pixel format, color range/space/primaries/transfer, and alpha behavior. Decode a real poster frame and test the target browser/editor. Record any known chunk-boundary alpha flicker and provide an opaque fallback.

## Failure prevention

- Keep straight/premultiplied alpha semantics consistent.
- Do not use JPEG intermediates for alpha assets.
- Avoid excessive contrast or saturation that reveals halos.
- Check the first, middle, settle, and final frames for black boxes or flicker.
- Test long enough playback to reveal chunk or loop-boundary issues.
- Verify the actual host supports the chosen alpha codec; a file extension is not a capability.
- Provide a static poster and opaque fallback when browser alpha support is uncertain.
