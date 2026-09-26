# Idle and Ambient Patterns

Define the resting, always-on state of an approved mark, the persistent behaviour permitted on top of it, and the interactive state set that replaces it on input.

## Contents

- Rest state
- IDLE-01 Rest to breathing loop
- IDLE-02 Orbit and rotor idle
- IDLE-03 Interactive state set
- IDLE-04 Scroll and scrub linkage
- Seamless looping
- Determinism
- Resource budget
- Accessibility
- Limits
- Failure modes
- QA

## Rest state

Treat the rest pose as the approved final state, frame-for-frame the state the reveal ends on. Define an idle loop as a rest state plus a duty cycle, not a continuous animation.

| Parameter | Working range | Basis |
|---|---:|---|
| Cycle length | 2.5–4.0 s | 75–120 frames at 30 fps; normally at or above the 3.0 s floor in `assets/motion-tokens.json` |
| Fully visible hold | 25–35% of cycle | stable reference for the eye |
| Motion amplitude | 0.5–2% of mark size | organic marks stay at 1–2% |
| Rotation | at most 2° per cycle | symmetric geometry only |

Ship a static state for any mark with no reason to move. Do not add an idle loop to satisfy an empty requirement; record it as a defect.

## Scenario blocks

### IDLE-01 Rest to breathing loop

**Intent:** keep a living mark present for long durations, without a story.

**Layers:** one group only — ring, monogram, or wordmark accent.

**Motion:** hold rest, breathe scale 1.00 to 1.01–1.02 and back.

**Timing:** 2.5–4.0 s at 30 fps; hold the visible state 25–35% of the cycle.

**Easing:** `organic` out, `settle` back, or a sine of the cycle.

**Anchors:** the mark's center of mass, not the bounding box.

**Risks:** no return to rest, drift over cycles, header fatigue, anchor error.

### IDLE-02 Orbit and rotor idle

**Intent:** suggest system activity, machinery, or continuous process.

**Layers:** one orbiting accent, one rotor element, its arc.

**Motion:** turn one element on a fixed path; offset a dash or Trim Paths 0 to −360°.

**Timing:** 3.0–8.0 s per revolution; one revolution per cycle, never 0.96 turns.

**Easing:** `path-linear`; easing a constant turn stalls at the wrap.

**Anchors:** the true geometric center of the arc.

**Risks:** asymmetric artwork spinning as symmetric, crawling dashes, an orbit clipping its ring.

### IDLE-03 Interactive state set

**Intent:** express hover, pressed, active, and selected without an animation per state.

**Layers:** the rest-state groups plus one highlight ring or fill accent.

**Motion:** change transform, opacity, or one colour property; hold all else at rest.

**Timing:** 90–180 ms in and out; hold the new state until the next input.

**Easing:** `enter` in, `settle` out.

**Anchors:** the IDLE-01 anchor, so a hovered mark never jumps.

**Risks:** motion as the only state signal, no focus parity, states out of phase.

### IDLE-04 Scroll and scrub linkage

**Intent:** couple a persistent mark to a page, gesture, or product state.

**Layers:** one or two groups, normally the IDLE-01 groups.

**Motion:** drive one normalized progress value from scroll or drag; run no second loop.

**Timing:** span 0–100% within one scroll viewport, then settle in 90–180 ms.

**Easing:** apply easing to the input, not the output, unless smoothed.

**Anchors:** the same anchor set; freezing scroll must return exactly to rest.

**Risks:** scrub fighting the cycle, a stuck mid-state, jitter, an unresolved endpoint.

## Seamless looping

Match the last state to the first in position, scale, rotation, colour, and alpha. Match velocity too, not just value. Do not duplicate the end keyframe; a repeated boundary frame is the most common cause of a hitch. Prefer a periodic function of the frame number over a spring plus a loop wrap.

```ts
const CYCLE = 90;                   // frames, 3.0 s at 30 fps
const t = (frame % CYCLE) / CYCLE;  // 0..1, wraps with no seam
const w = 0.5 + 0.5 * Math.sin(t * Math.PI * 2);
```

Set the cycle to a whole number of frames, rounding seconds as `round(sec * fps) / fps`. Where a spring is used, measure its natural duration in frames and make the period an exact multiple, otherwise the tail truncates and pops. Set a work area to `[0, N)`.

```text
[ 0, 30)  hold    rest state, fully visible, no transform
[30, 60)  motion  excursion out to peak amplitude
[60, 90)  reset   return to rest; frame 90 wraps to frame 0
```

## Determinism

Make every animated value a pure function of the frame number and props; frame renderers evaluate a frame repeatedly, in parallel, and out of order. Do not use `Math.random()`, wall-clock time, or module-scope counters; replace runtime randomness with a seeded generator keyed on a stable string. Treat `time` and `sin`/`cos` of `time` in After Effects as acceptable and `wiggle()` as unreproducible across a re-creation. Bake Lottie and dotLottie keyframes, and assume neither player reads an OS motion preference (`accessibility-and-reduced-motion.md`).

## Resource budget

Prefer transform and opacity. Avoid per-frame filters and large blurs, keep the animated area small, suspend the loop off-screen, and provide a static fallback for low-power devices. A header mark should normally consume at most 0.5% of the frame budget; measure this, do not assume it.

**Forbidden shortcuts:** unthrottled `requestAnimationFrame` driving, per-frame `filter: blur()`, a full-canvas glow behind a header logo.

## Accessibility

Hold the approved final frame as the reduced-motion rest state, indefinitely, with no dissolve longer than about 150 ms. Keep interaction motion inside 90–180 ms. Make every idle loop pausable and document the control. Do not preserve scale, rotation, or orbit merely because the change is described as subtle. Assume the host selects the static asset.

## Limits

Do not add an idle loop to a static brand asset, a mark on screen for under 2 s, dense artwork where 0.5–2% motion destroys legibility, or any context where motion competes with content. Ship the rest state alone.

## Failure modes

- **Boundary hitch.** **Symptom:** a tick once per cycle. **Repair:** delete the duplicated end keyframe, confirm velocity parity, use the modulo form.
- **Accumulating drift.** **Symptom:** the mark wanders across minutes of uptime. **Repair:** re-derive values from the frame number, re-verify the anchor.
- **Unseeded variation.** **Symptom:** a re-render differs from the last. **Repair:** seed on a stable string, bake the sample table.
- **Persistent overspend.** **Symptom:** frame drops, heat, battery loss. **Repair:** cut animated area, fall back to static, record the cost.

## QA

- Loop a rendered cycle 20 times; confirm frame N matches frame N+90 within 1/255 per channel.
- Measure first-frame and final-frame delta for position, scale, rotation, colour, and alpha.
- Record animated area as a share of the viewport and of the frame budget on the lowest device.
- Compare the rest state to the approved master frame, with no residual guide or blur.
- Confirm the host selects the static asset under reduced motion, and that pause works from the keyboard.
- Scrub to 0% and 100% and confirm the mark resolves to rest at both ends.

Budgets and the reduced-motion mapping are inferred; the source's idle and reduced-motion sections are blocked in the extract, so treat the numeric targets as provisional until measured.
