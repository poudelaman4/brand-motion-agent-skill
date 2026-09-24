# Review Matrix

## Contents

- Required matrix
- Encoded-output checks
- Evidence to retain
- Related files

## Required matrix

| Dimension | Minimum checks |
|---|---|
| Timeline | exact frame 0, early checkpoint, midpoint, late checkpoint, settle frame, poster frame, and one frame before settle |
| Scale | 16, 32, 64, 128 px, and actual delivery size |
| Background | white, near-white, black, checkerboard, brand color, photography |
| Format | source, decoded encoded output, target player/editor |
| Typography | exact glyphs, kerning, counters, baseline, reading direction |
| Layer integrity | each layer alone and full composite |
| Performance | low-end device, memory, console/decode errors, render time |
| Accessibility | reduced motion, keyboard/focus, no flashing, host asset selection |
| Loop | first/last state, seam, velocity, color, and duplicate-endpoint behavior |
| Color | ICC profile, color range/space/primaries/transfer, codec tolerance |
| Audio | sync, levels, optional delivery, voice/music/SFX separation when relevant |
| Platform | recompression, safe area, thumbnail readability, upload duration limits |

## Encoded-output checks

- Probe stream metadata: frame count, fps, duration, codec, pixel format, color range/profile, and alpha mode.
- Decode the exact poster frame from the encoded file; do not rely only on a composition still.
- Compare canonical geometry and alpha separately from color-managed RGB output.
- Use a documented tolerance for lossy H.264/WebM and resampling. Do not claim byte identity.
- Test an opaque fallback when alpha support is uncertain.
- Check the actual host's reduced-motion branch; CSS media queries do not automatically stop arbitrary video or Lottie playback.

## Evidence to retain

Keep the source checksum and profile, motion brief, manifest, render command, dependency versions, exact checkpoint contact sheet, decoded poster frame, stream metadata, final-state comparison JSON, and a short pass/warn/blocked report.

See `qa-checklist.md` for the full gate list and `failure-catalog.md` for diagnosis and repair.
