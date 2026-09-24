# Wordmark and Lockup Patterns

## Contents

- WORD-01 Tracking settle
- WORD-02 Directional mask
- WORD-03 Write-on
- WORD-04 Mark-to-lockup
- Parallel timing
- Typography rules
- QA

## WORD-01 — Tracking settle

Fade the approved wordmark in while a documented `letter_spacing` or glyph-position delta contracts from 1.08–1.20× the approved value to the master kerning. Use only when the source supports editable or outlined glyph groups with exact spacing.

**Timing:** 0.8–1.4 s; hold 500–800 ms.

**Risk:** looking like font substitution or broken typography.

## WORD-02 — Directional mask

Reveal the wordmark through a brand-native horizontal, vertical, or logo-derived mask. Keep the mask direction semantically meaningful and avoid arbitrary mid-glyph clipping.

**Timing:** 0.6–1.1 s; main word 0–750 ms; descriptor 450–950 ms.

## WORD-03 — Write-on

Trace approved letterforms in writing order and optionally hand off from stroke to fill. This requires an approved stroke skeleton or text-on-path construction; filled glyph outlines alone do not provide a reliable writing order. Never fake a handwriting style on an unrelated logo.

**Timing:** 1.2–2.2 s; drawing 0–1500 ms; fill handoff 700–1700 ms.

## WORD-04 — Mark-to-lockup

Resolve the symbol first, then bring in the wordmark. Keep the mark stable while text settles. This is often the safest premium pattern.

**Timing:** 1.0–1.8 s; mark 0–900 ms; wordmark 500–1400 ms; hold.

## Parallel timing

The wordmark does not need to wait for every leaf or module to stop. It can begin once the primary silhouette is readable, creating overlap and a more natural 2–4 second sequence.

For a generic 4-second 30 fps mark-to-lockup sequence:

```text
frame 0       core symbol begins
frames 4–34   first supporting groups begin
frames 13–45  second supporting groups follow
frame 30      wordmark begins, staggered by a small frame offset
frame 48      descriptor/rule follows if present
frame 64      lockup mostly settled
frame 96      canonical final state guaranteed
frames 96–119 hold
```

Use actual source geometry and adjust stagger based on letter width and language direction. If the wordmark is a single outlined group, use a quiet mask or fade instead of fake per-letter motion.

## Typography rules

- Preserve exact kerning, counters, baseline, and clear space.
- Outline or embed fonts for rendering.
- Keep left-to-right, right-to-left, vertical, and non-Latin requirements explicit.
- Do not use a live font that might substitute on the target machine.
- Avoid bouncing every letter; one wordmark-level settle usually looks more premium.
- Keep the descriptor subordinate and readable.

## QA

- Compare final text silhouette to the approved master.
- Check that no glyph clips during mask or scale motion.
- Verify reading order and language direction.
- Inspect the wordmark over every required background.
- Confirm the mark is recognizable before the wordmark completes.
- Provide a static poster and reduced-motion state.
