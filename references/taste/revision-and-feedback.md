# Revision and Feedback

The workflow is linear through the first build, then it is not. A reviewer returns a sentence, and the agent has to turn it into a parameter change without renegotiating the brief, without touching canonical geometry, and without quietly discarding a veto it already earned. This file is that loop.

## Contents

- The loop
- Read the comment
- Map to a change
- What a revision may not touch
- When a comment is a new brief
- Conflicts
- After the change
- QA

## The loop

1. **Read the comment, do not execute it.** Restate the symptom in the vocabulary of `references/taste/quality-tests.md` before changing anything.
2. **Name the cause.** The vocabulary table pairs each symptom with a usual cause; confirm the cause against the build rather than accepting the pairing as diagnosis.
3. **Change one thing.** One token, one curve, one hold. Two changes at once make the next comment unreadable.
4. **Re-render the checkpoints.** The same frames as before, so the difference is attributable to the change.
5. **Answer the comment with evidence.** State what changed, in what units, and show the checkpoint that proves it.
6. **Record the departure.** A revision that leaves the documented default is a decision with both sides named; see `references/delivery/motion-system-and-handoff.md`.

Never reply to feedback with a new export and no diff. "Updated" is not an answer to a comment; "the hold went from 400 ms to 700 ms, settling at frame 96" is.

## Read the comment

Reviewer sentences are not parameters. Translate before acting.

| The comment says | Restate it as | Verify against |
|---|---|---|
| Make it feel more premium | Which register term is missing: restraint, negative space, or pacing | `references/taste/brand-register.md` |
| It feels cheap | Reads as a template, over-eased, or too bouncy | `references/taste/quality-tests.md` |
| Too fast | Energy registers, mark unseen | Duration against the frequency ceiling |
| Too slow | Self-important | Duration against the reading floor |
| The logo reads late | Hold start frame is after the reading floor | `references/craft/pace-and-rhythm.md` |
| The easing is weird | Under-eased, over-eased, dead stop, or popping | The four easing symptoms in the vocabulary |
| Something feels off | Ask which term applies before changing anything | Do not act on this sentence alone |
| Make it pop | Competing focal point, or a missing primary action | Focal ranking in the build |
| Try it with particles | A technique change, not a revision | Step 4 below, and the register veto |

The row for `Something feels off` is the commonest case. When the comment names no symptom, ask for the term before changing a parameter; a change made against an unnamed symptom is unverifiable, and the next comment arrives on top of it.

## Map to a change

Change the smallest lever that produces the named symptom's cause.

| Cause | Lever | Where the value lives |
|---|---|---|
| Too fast or too slow | Total duration | `duration` in `assets/motion-tokens.json`, scaled by frequency |
| Too bouncy | Overshoot | `overshoot` ceiling for the register |
| Over-eased or under-eased | The easing curve | `easing` for that transition |
| No rest | Hold frame or final hold | `hold_start_frame`, `settle_frame` |
| Mechanical | Stagger or per-element offset | `stagger` |
| No hierarchy | Rank the primary action and drop the others to supporting | The build, not a token |
| Reads late | Move the hold start earlier, or shorten the opening | Milestone frame in the brief |
| Competing focal point | Remove the secondary effect, do not dim it | The build |

Two rules hold on every one of these. First, the duration change must stay inside the frequency ceiling and above the reading floor; if the requested duration leaves that band, it is a conflict and belongs in the conflicts section below. Second, do not reach for blur, glow, or particles to satisfy a pacing comment. Those are the defaults a reviewer already rejected when they read the motion as cheap.

## What a revision may not touch

These are settled by the brief and are not open to a revision unless the comment explicitly renegotiates the brief.

- Approved path and shape geometry
- Counters, kerning, and the fixed lockup relationships
- The canonical final state and its comparison tolerance
- Clear space and the bounding box
- Brand colour, unless the comment is itself about brand colour
- The register and the techniques it vetoed
- The reduced-motion state
- The delivery matrix and its covered zones
- A hard blocker already recorded

A comment that requires changing one of these is not a revision. It is a new brief, and it needs a new intake.

## When a comment is a new brief

Stop the loop and re-run intake when the comment:

- Names a different technique than the one built
- Changes the brand register, or arrives as a register claim the earlier inference did not have
- Changes the source file or the approved artwork
- Changes the delivery context, platform, or runtime
- Changes the runtime duration by more than a factor of two
- Contradicts a register veto the agent already applied
- Asks for something the feasibility gate ruled out

Say which of these it is and re-run the workflow from that step rather than the intake from scratch. Re-running only the affected step is normally enough; a register change is the exception, because taste gates sit downstream of classification.

## Conflicts

A comment can be impossible as stated. Report the conflict with both sides named rather than silently choosing one.

| Conflict | Report as |
|---|---|
| Requested duration is under the reading floor for the wordmark | The floor, the request, and the shortest compliant value |
| Requested duration is over the frequency ceiling | The ceiling, the request, and the longest compliant value |
| Requested overshoot exceeds the register ceiling | The register, the ceiling, and the requested value |
| Requested technique is vetoed by the register | The register and the veto reason from the taste gate |
| Requested technique is gated off by the source | The gate code from the profiler output |
| Request is blocked by the environment | The capability, its state, and the install command or fallback |

Never satisfy a comment by widening a documented ceiling. The ceiling is the argument; widening it is how the package loses the taste gate it just built.

## After the change

- Re-run the profiler only if the comment was about the source or a register; a timing change does not re-profile.
- Re-validate the manifest if any field it checks moved.
- Re-render the checkpoint sheet, not only the final frame; the comment is normally about the middle.
- Re-run the final-state comparison if the change touched any transform that is part of the canonical state.
- Carry the changed value into the manifest, not only into the render, or the next revision starts from a stale value.

## QA

- [ ] The comment was restated as a named symptom before any value changed
- [ ] Exactly one lever changed, and its previous and new values are both stated with units
- [ ] The new value sits inside the frequency ceiling and above the reading floor
- [ ] No canonical invariant moved
- [ ] Checkpoints were re-rendered and the difference is visible
- [ ] A departure from a documented default is recorded as a decision with both sides named
- [ ] Any impossible request is reported as a conflict, not absorbed
