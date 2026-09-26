# Pace and Rhythm

Control when things move and when they stop. Duration is the least important of the four dials, and getting it wrong is why a reveal feels sluggish while technically playing at speed.

## Contents

- Four words that are not one
- The reading floor
- Why the same duration feels different
- Rhythm
- Sync
- Editing and the cut
- Anticipation and follow-through
- Frame budgets
- Limits
- Failure modes
- QA

## Four words that are not one

| Term | Definition | Unit | Changed by |
|---|---|---|---|
| Duration | How long one event occupies | ms or frames | The keyframe pair |
| Pace | How fast a thing travels | units/s, px/s, degrees/s | The speed curve |
| Tempo | How often events occur | events/s | The interval between them |
| Rhythm | The pattern of intervals, accents, and rests | a pattern over time | The arrangement |

The diagnostic error is treating them as one dial. Lengthening the gap before a move raises tempo while leaving the move slow; shortening the move while keeping the gap raises pace only. Both read as rushed but sluggish. To make a mark feel faster, shorten the move and compress the gaps, and check both.

| Intent | After Effects | Remotion | CSS |
|---|---|---|---|
| Total length | Composition duration | `durationInFrames` | `animation-duration` |
| Per-element length | Layer in and out points | `<Sequence durationInFrames>` | `animation-duration` |
| Freeze or rest | Time remapping with a hold keyframe | `interpolate` with a clamped right edge | `animation-fill-mode: forwards` with `steps()` |
| Gap between events | Layer `startTime` | `<Sequence from>` | `animation-delay` |

## The reading floor

Reading speed gives a floor, and the naive version of it is wrong. English silent reading averages 238 wpm at about 4.76 characters per word, which is 18.9 characters per second. Dividing an 8-character wordmark by that gives 423 ms, and a wordmark built to that figure feels like it flashed past.

A single discrete wordmark arriving cold is not prose. It gets no syntactic prediction and no preceding saccade runway, so it needs two or three fixations at 200–250 ms each before any recognition happens. Use the composite floor:

```text
T_read(N) = 200 ms + N * 68 ms + 400 ms
N is the character count of the wordmark that must be read
```

| Characters | T_read | Frames at 30 fps |
|---:|---:|---:|
| 3 | 804 ms | 25 |
| 6 | 1008 ms | 31 |
| 8 | 1144 ms | 35 |
| 13 | 1484 ms | 45 |
| 21 | 2028 ms | 61 |

The 400 ms consolidation term is `provisional`. The 200 ms fixation and 68 ms per-character terms are `observed`. The gap between this floor and the naive figure is roughly 2.7× for an 8-character wordmark, and that multiplier is the whole reason a correctly-paced reveal still feels fast.

Apply it as a hard constraint. A 60-frame stinger at 30 fps supports a wordmark of three characters or fewer. A 6–8 character wordmark in a 60-frame stinger cannot meet the floor: ship the mark without the wordmark, extend to 75–90 frames, or accept the wordmark is decorative and say so.

## Why the same duration feels different

Mean velocity is identical for every easing curve over the same two points. What differs is distribution. The perceived end of a move is the last frame where change stays above roughly one sixtieth of mean velocity; below that the eye integrates it as arrived while the clock keeps running.

| Ease-out curve | Peak/mean velocity | Duration spent below the perception threshold |
|---|---:|---:|
| sine out | 1.57× | 0.65% |
| quad out | 2.00× | 0.83% |
| cubic out | 3.00× | 7.45% |
| quart out | 4.00× | 16.1% |
| quint out | 5.00× | **24.0%** |
| expo out | 6.93× | 13.0% |

The one-sixtieth threshold is `[UNVERIFIED]`. Read the table as a warning about the curve everyone reaches for. A quint out is chosen because it feels snappy, and it also hides a quarter of its own duration: a 500 ms quint out is a 380 ms event with 120 ms of nothing after it. An expo out has a higher peak and hides less time, which makes it the better curve for a mark.

Where a cubic-bezier curve's energy actually lives is at its endpoints. The initial slope is three times the first control-point rise, and the final slope is three times the last:

```text
cubic-bezier(0.05, 0.7, 0.1, 1)   launch 42x, arrival 0    a hard launch into a perfect rest
cubic-bezier(0.16, 1,   0.3, 1)   launch 18.75x, arrival 0
cubic-bezier(0.3,  0,   0.8, 0.15) launch 0, arrival 12.75x a hard exit
```

Acceleration and deceleration should be asymmetric. An entrance that launches hard and settles soft reads as confident; the reverse reads as apologetic. Exits are shorter than entrances and accelerate, so a departing element cannot be retrieved.

One flagship curve deserves a warning. The Material 3 emphasized curve is a two-segment path, not a cubic-bezier, and sampled it is already 96.5% complete at 56% of its duration. The remaining 44% of a 500 ms emphasized transition is a settle. Use the decelerate variant for an entrance, not the emphasized variant, or pay 500 ms for a 280 ms arrival.

## Rhythm

Rhythm comes from the arrangement of intervals, not from their individual durations.

- **Stagger direction reads as intent.** An even stagger reads as machine-assembled. A decelerating stagger, where each element starts slightly sooner than the last, reads as one gesture accelerating. An accelerating stagger reads as assembly under strain.
- **Group before staggering.** Move elements together in meaningful groups of two to four, then offset the groups. Staggering twelve elements by index produces a queue, not a composition.
- **Accent one element.** In a multi-part reveal exactly one element should lead and the rest should support. Without an accent the eye has no entry point and the whole thing reads as simultaneous.
- **The off-beat accent is a risk.** Displacing one element off the grid reads as intentional only when the rest of the rhythm is strict. In a 1–2 second reveal there is no time to establish the grid, so an off-beat accent reads as a mistake.
- **Beat-grid alignment** matters when there is audio. With no audio, an even grid plus one accent is the safest rhythm available.

## Sync

With a soundtrack, mark the structure before marking the motion: bar, beat, and phrase, then choose which animation beats land on hits. A reveal that resolves on the downbeat of the first phrase reads as intentional; one that resolves mid-bar reads as mistimed.

Keep audio-driven animation deterministic. Every value must remain a pure function of the frame or of a stable input, so two renders of the same frame range are identical. An audio-reactive value sampled at render time is not reproducible.

With no audio, sync to a structural event instead: the click that triggered the state, the completion of a load, the scroll position that triggered a reveal. UI event sync is more reliable than musical sync and usually more appropriate.

## Editing and the cut

| Treatment | Use when | Cost |
|---|---|---|
| Straight cut | The mark is done and content begins | Free, and the default |
| Dissolve | Two states must cross-fade and no third geometry exists | 150–300 ms |
| Dip to black or white | The piece is a discrete chapter, not a transition | 200–400 ms and a full frame of dead time |
| Hold on the final frame | The mark must be readable or held indefinitely | 500–1000 ms minimum |

Frame rate changes perceived pace more than duration does. 24 fps reads as filmic and slightly soft, 30 reads as neutral and is the safe default, 50 and 60 read as immediate and are appropriate for UI and short-form. Conforming between them changes the feel of an existing animation, so decide the rate before authoring, not after.

Hold frames and repeated frames are not the same. A duplicated final keyframe produces one extra frame of nothing at the seam, which is the single most common cause of a visible loop hitch. In a seamless loop, delete the final keyframe rather than matching it.

Time remapping and retiming are legitimate but must be reported: a retimed animation is a new animation for every downstream check, including the final-frame comparison.

## Anticipation and follow-through

The animation principles apply to a brand mark unevenly. These transfer cleanly:

| Principle | Frame budget | Fit |
|---|---:|---|
| Staging | n/a | Always. One element in focus at a time. |
| Overlapping action | 40–70 ms offset | Always. Never a synchronised block. |
| Arcs | n/a | Always. Movement follows a curve, never a straight interpolation. |
| Follow-through and settle | 100–200 ms | Almost always. This is what gives a mark mass. |
| Anticipation | 60–120 ms | Rarely. Reads as a cartoon wind-up on a still object. |
| Exaggeration | n/a | Never on identity geometry. At most 8% on an explicitly playful accent. |
| Squash and stretch | 2–4% | Only on a character or organic form, never on a wordmark. |
| Smears | n/a | Never in a brand mark. |

Anticipation is the one most often added and most often wrong. A wind-up implies the mark is about to be struck, which is a claim about physical event, and a static identity has made no such claim. Follow-through is the opposite case: a short settle after arrival costs 100–200 ms and is what separates a mark that has weight from a mark that merely stopped.

## Frame budgets

One-shot reveal, 120 frames at 30 fps, 4.000 s, 8-character wordmark:

```text
0-6      pre-roll vacuum; nothing on screen
6-24     primary mark gesture, 600 ms
24-30    hold while the mark is readable
30-66    wordmark build, 1200 ms; T_read floor is 1144 ms
66-96    settle and overshoot decay
96-120   final hold, 800 ms
```

Fast stinger, 60 frames at 30 fps, 2.000 s, three characters maximum:

```text
0-3      pre-roll vacuum
3-24     primary mark gesture, 700 ms
24-36    wordmark, 400 ms; T_read floor for 3 characters is 804 ms - not met
36-48    settle
48-60    final hold, 400 ms
```

The stinger budget states its own failure: at 60 frames a wordmark over three characters cannot be read. Either drop the wordmark, extend, or record the wordmark as decorative.

Seamless loop, 90 frames at 30 fps, 3.000 s:

```text
0-28     visible hold, 28% of the cycle
28-66    primary motion, 1270 ms
66-76    exit toward the rest state, 330 ms
76-90    dead time before the seam, 470 ms
```

The seam is the last frame meeting the first, and the return leg must be the exact inverse of the outbound leg including easing, or the loop pops.

## Limits

- Cut an element rather than extending the hold when the total exceeds the delivery ceiling. A longer reveal is not a better reveal.
- Do not use duration to disguise a weak concept. If a concept needs four seconds to read as intentional, it is the concept that is wrong.
- Do not author a bespoke timing model for an asset that will be seen once. A token from the system is correct there.
- Never let the reading floor be met by slowing the mark down. Slow the entrance, or hold longer, but never reduce the time the wordmark is at full contrast.
- Stop using curves whose tail exceeds about a quarter of the duration for anything but an ambient loop.

## Failure modes

**Symptom:** the wordmark is on screen for 300 ms and nobody reads it. **Repair:** apply the reading floor and either extend the hold, shorten the wordmark, or drop it from this deliverable.

**Symptom:** the animation plays at the right speed but reads as sluggish. **Repair:** the gap is carrying the tempo while the move carries none. Shorten the move and compress the gap, and check the curve's tail fraction.

**Symptom:** a seamless loop hitches once per cycle. **Repair:** the final keyframe is duplicated. Delete it so the last frame and the first frame are the same frame.

**Symptom:** every element lands together and the reveal reads as a single flash. **Repair:** there is no accent and no stagger. Offset the supporting group by 40–70 ms and lead with exactly one element.

## QA

- [ ] The wordmark's on-screen duration at full contrast is at or above the reading floor for its character count.
- [ ] The total duration is inside the delivery ceiling and the sequence contains a rest beat.
- [ ] The curve's imperceptible tail is under about a quarter of the duration, or the move is an intentional ambient loop.
- [ ] Entrance and exit are asymmetric, with the exit shorter and accelerating.
- [ ] A seamless loop has no duplicated end frame, and the return leg mirrors the outbound leg exactly.
- [ ] The frame rate was chosen before authoring and recorded in the manifest.

These are planning ranges, not a reason to slow a mark down to prove a point.
