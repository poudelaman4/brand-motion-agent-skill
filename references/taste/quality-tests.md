# Quality Tests

Judge whether brand motion is sound, not good; every test must be runnable by someone who did not make it.

## Contents

- Quality tests
- Reading a piece
- What expensive looks like
- Review vocabulary
- Justifying a choice
- Limits
- QA

## Quality tests

Run all thirteen. Failing one means revisiting a decision; failing four means it is wrong.

| Test | How to run it | Pass criterion |
|---|---|---|
| Thumbnail | Freeze 3 frames at 1 s in beside competitors at 200 px | Own frame wins; no mid-frame beats the final |
| Still frame | Freeze 10 random frames; view each alone | All 10 read as a logo, not debris `[UNVERIFIED]` count |
| Two-second | Time first identification, not completion | Identifiable by 2.0 s; nothing continues after |
| Squint | Blur the frame; count regions still moving | Exactly 1 region reads |
| Greyscale | Desaturate the piece | Structure survives; no hue shift carries it |
| Small size | Render at 240 px and 32 px; 100 px for a hero | Identifiable at both, core mechanism visible |
| Silent | Watch 3 times muted | Reveal, timing, and settle hold without a whoosh |
| Frame one against frame final | Place both side by side | Final frame wins, matches the master; 98% assembled fails |
| Loop seam | Play 10 s; inspect last 5 into first 5 frames | No hitch, contact duplicate, colour pop, or velocity break |
| Negative space | Step the transition; inspect every counter | No counter opens, closes, or shaves |
| Reduced motion | Enable OS reduce-motion; run the asset | Brand legible; nothing carried by movement |
| Target player | Open the encoded file in the delivery player | Plays at 30 fps; no missing asset or alpha fault |
| Showreel against product | Place at 240 px inside the real product | Survives the product; a showreel-only read fails |

## Reading a piece

Run the cheap disqualifying checks first; stop at the first failure.

1. Compare the final frame against the static master.
2. Confirm legibility at 32 px.
3. Confirm it reads at 40 px.
4. Confirm the duration sits inside the ceiling, normally ≤2.5 s.
5. Count the primary gestures; require exactly 1.
6. Step the transition; inspect every counter.
7. Swap in a same-style mark; the motion must stop belonging.
8. Score the register one axis at a time, per `taste/brand-register.md`.

## What expensive looks like

| Signal | Why it works |
|---|---|
| One thing moves, then there is rest | Rest reads as evidence of a decision |
| It ends on a held readable frame | A designed frame survives every screenshot |
| One custom curve; exits shorter than entrances | Library defaults belong to nobody |
| No linear; duration scales with travel and mass | Linear reads as an unmindful animator |
| Motion comes out of the mark's geometry | Hardest to fake, clearest discriminator |
| Negative space survives the transition | Counters closing mid-move is the amateur tell |
| A rest state plus a shipped still frame | Someone planned where motion cannot play |
| Sound load-bearing; all of it works muted | Muted survival is the only audio rule |

The mirror list reads cheap: one transform on everything; effects layered on the mark instead of from it; overshoot with no physical referent; length exceeding the job; fading out instead of settling; one library easing throughout; illegible at 240 px; no still frame; a showreel entry that fails in the product.

## Review vocabulary

Use these terms instead of cheap or not on brand; each names a symptom two reviewers would agree on.

| Term | Visual symptom | Usual cause |
|---|---|---|
| Too bouncy | Overshoot passes ~15%, never settles | Spring from UI |
| Too fast | Energy registers, mark unseen | UI duration range |
| Too slow | Self-important; viewer leaves early | No published ceiling |
| Too busy | The eye cannot settle | Main action, 3 secondaries |
| Fighting itself | Mark scales as the type slides the same way | Lockup built after |
| No rest | Nothing is ever still | No hold frame |
| Reads as a template | Seen on a competitor this month | Stock library move |
| No hierarchy | Every element treated identically | One transform, equal items |
| Mushy | Soft edges; phases blur together | Excess blur, overlap |
| Floaty | Light but unattached | Weightless easing |
| Mechanical | Everything moves identically | Uniform rhythm |
| Over-eased | The object hovers, never commits | Long ease-in-out |
| Under-eased | Stall at start, jolt at end | ease-in on entrance |
| Competing focal point | Two elements equally loud | Mark and type both effected |
| Ambiguous focal point | All quiet, nothing leads | Restraint without ranking |
| No negative space | A counter closes, mark illegible | Move on the bounding box |
| Snapping | Instant change, no continuity | Dropped keyframe or cut |
| Popping | Jump between near-identical states | Extreme curve between keys |
| Swimming | Something drifts during a hold | Shallow tangents |
| Drifting | Slow creep, normally on a loop | Unanchored ambient loop |
| Dead stop | Motion arrives and ceases | ease-in on arrival |
| Mushy settle | Landing smears, no contact | Deceleration too long |
| Premature payoff | Reveal completes, then continues | No still frame designed |

## Justifying a choice

Apply the referent test in order: name the move, the referent (physical, structural, historical, or semiotic), the duration, and the frequency to survive.

```text
It draws in 1.1 s, because the nib curve built the mark, and it stops: nobody
watches a signature twice. (structural)

It overshoots 6%, because the character has rubber in it and the brand claims
play, on a screen seen twice a year. (physical)

It wipes from the aperture, because the 1968 mark was drawn around a lens
iris, and it holds 400 ms. (historical)

Refuse 3.4 s: play the 30th viewing; a viewer who skips has answered. Offer 1.4 s.
Refuse 18% overshoot until the rubber is named. Otherwise ship 0%.
```

## Limits

Judge soundness here; judge goodness in `taste/brand-register.md`.

- Accept that passing every test can leave a piece forgettable.
- Reject the claim that these tests replace a register decision.
- Redesign the mark, not the motion, when 32 px fails.
- Record a negative-space failure as a redesign, not a motion tweak.

## QA

- Require the still-frame test with all 10 frozen frames attached.
- Require the small-size test to state widths: 240 px, 100 px, 32 px.
- Require the frame-one and frame-final comparison, with a pixel delta.
- Require the squint test to report a count of 1, not an impression.
- Require the target-player test, per `qa/review-matrix.md`.
- Require the showreel-versus-product test before calling a piece finished.

Treat every criterion here as provisional until it survives review by someone who did not make the piece.
