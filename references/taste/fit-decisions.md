# Fit Decisions

Resolve a motion choice by running a fixed procedure, and record the losing options beside the winner.

## Contents

- Contents
- The decision procedure
- Precedence
- Justifying a choice
- Saying no
- When to ask
- Writing the motion guideline
- Publishing the motion
- Limits
- QA

## The decision procedure

Run the eight steps in order; the early steps carry vetoes and the later steps only trim.

1. Confirm the deliverable and its frequency budget. Name the mode from `taxonomy.md`, count views per person monthly, and take the tighter of that row and the mode ceiling.
2. Read the brand register. Locate the row in `taste/brand-register.md`; confirm it against a claim quoted from the positioning, not a mood word.
3. Run the structural profile. Apply `technique-selection.md` and record what it gated; settle a gated technique as impossible before consulting taste.
4. Apply the register's veto list. Read the fatal move and the three cheapeners as prohibitions, not cautions.
5. Consult the register's preferred vocabulary. Choose one primary technique from the rows surviving steps 3 and 4; record the rejected candidates.
6. Run the cliché check. Reject a templated move carrying no brand-specific information, per `taste/cliche-and-restraint.md`.
7. Budget the pacing. Set duration from the frequency row and the register ceiling; hold the exit 50–100 ms shorter than the entrance.
8. Run the tests in `taste/quality-tests.md` and record numbers, not impressions.

Treat structure as subordinate to register: carry a forbidden opportunity forward as a note, unless the structural fact is itself the stated claim.

## Precedence

Apply this order when two rules collide; read downward.

```text
1  explicit user instruction    beats every rule below
2  legal or regulatory minimum  beats any brand preference
3  platform guideline           beats any brand preference
4  stated brand claim           beats an inferred register
5  pacing budget                beats a technique's natural duration
6  register veto                beats a structural opportunity
7  brand preference             beats template convention
8  structural opportunity       advisory; lowest
```

Write every conflict resolved against the recommendation into `decision_log` in `assets/motion-brief-template.json`, naming both sides. Treat a silent drop as an open question returning next revision.

## Justifying a choice

Write one sentence naming the move, the referent, the duration, and the frequency the piece must survive.

```text
It settles from 0.94 over 900 ms, because a half-step back is how a person
stands at a distance, and it must survive ~50 views a month. (physical)

It wipes from the aperture, because the 1954 mark was drawn around a lens
iris, and it holds 400 ms. (historical)

It builds counter before stem, because that is the ink order, and it runs
once per video at 1.4 s. (structural)

It holds flat, because a bank promises stability while a settle promises
arrival, and it stays under 1.0 s. (semiotic)
```

Reject two failure forms: a justification with no referent, since a mood word can be neither checked nor improved; and a justification listing three reasons, since three mean the referent was never found.

## Saying no

Refuse in the shape below, with a reason the requester can act on.

```text
intent   name the job the request serves
cost     one number, one named conflict
offer    name the nearest asset that works, with its duration

request  "premium-feeling ident for the stage"
answer   It plays before 140 videos a year, so each viewer sees it ~30
         times; a 3.4 s personality fails past the 10th viewing. Ship the
         1.4 s resolve; hold 3.0 s for the launch screen.
```

Reject three forms: a flat refusal with no alternative, which relocates the decision; a yes that quietly delivers something else, leaving brief and file disagreeing; a deferral leaving the decision unmade, which returns as drift. Offer the check rather than the opinion wherever a taste argument cannot be won.

## When to ask

Infer and document rather than asking: the register, the frequency budget, and the primary gesture. Record each as `provisional` and continue while no hard blocker in `intake-and-planning.md` remains.

Ask before proceeding: a second primary gesture, since the ceilings in `taste/brand-register.md` permit exactly one; any sound cue, including a whoosh; any departure from a published brand guideline, quoting the clause.

## Writing the motion guideline

Write the guideline as this procedure's deliverable, not an appendix. Draw the section structure from published brand systems: a shared language; what motion is for; the named curves as values; durations by purpose and frequency; logo animations; type animations; transitions; interface motion; and an explicit do-and-do-not list. Require 3–7 principles, each with one line of consequence; record the rejected options.

Constrain every default the silence permits.

| Default a silent document produces | Constraint that prevents it | Value |
|---|---|---:|
| Library default easing | Publish 3 curves as cubic-bezier; prohibit `ease` and `ease-in-out` as defaults | 0 permitted |
| One duration everywhere | Scale duration with travel and covered area | 4–6 tokens |
| Gives the exit the entrance's weight | Exit accelerates and runs shorter | 50–100 ms shorter |
| Accelerating curve on an entrance | Prohibit ease-in on entrances | 0 |
| Linear curve | Prohibit linear | 0 |
| Bounce on a utility action | Reserve bounce for brand surfaces | 0 in interface |
| Starts at zero scale | Open at 0.90 or higher | ≥0.90 |
| Ends by fading out | Land on the still frame, shipped as 2× PNG with alpha | 1 frame |
| Runs long | Publish a hard ceiling per mode | ≤3.0 s |
| Skips the small-size check | Publish a minimum size; loaders 24 px | ≥32 px |
| Skips the reduced-motion asset | Ship a substitute per mode | 1 per mode |
| Adds an unapproved sound cue | Publish a position on sound, including none | 0 |
| Leaves a loop seam | Publish loop rules and a seam test | Seamless at 10 s |
| Hand-lays a keyframe against a rule | Publish motion in the tool, easing locked | Locked per template |

## Publishing the motion

Ship the tokens where the work already happens: duration, delay, and curve values as CSS custom properties or a JSON token file the build reads. Treat a PDF that cannot show easing as read once and closed.

Treat a document nobody reopens as not a system: version it, name an owner, publish a changelog, route uncovered cases there.

Require two motion modes, utility against brand: one curve cannot serve both a button and a title sequence.

## Limits

Stop the procedure where it cannot decide. Stop with two registers in tension and no stated claim to separate them; treat premium against bold and technology against technical precision as genuine pairs. Stop with a new technique carrying no precedent, and build one. Stop when the identity is itself unresolved: positioning, palette, or type still moving.

Treat unresolved identity as not a motion problem. Ship a static mark and settle the identity.

## QA

- Confirm the record names the register row, the frequency row, and the quoted claim, in that order.
- Confirm each rejected candidate appears in `decision_log` with the rule that rejected it.
- Confirm the primary technique count reads exactly 1 and the duration sits under the tighter ceiling.
- Confirm each justification carries one referent and one duration, with no mood word surviving.
- Confirm the still frame, the reduced-motion asset, and the 32 px check exist as files.
- Confirm the guideline carries a version, an owner, and a changelog entry.

Treat the precedence order and section structure as `observed` from published brand systems and the thresholds as `inferred` rather than measured; hold the procedure `provisional` until a commission tests it.
