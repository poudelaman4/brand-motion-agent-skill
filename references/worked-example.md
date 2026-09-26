# Worked Example

One logo, taken through the whole pipeline with the actual tool output. Read it to see how the steps compose and, more usefully, to see where the tools overrule the obvious answer. Every number here is the real output of the scripts in this package.

The source is `evals/files/layered-mark.svg`, run as:

```bash
python scripts/profile_logo.py evals/files/layered-mark.svg \
  --register premium --frequency occasional --draw-plan
```

## Contents

- The source
- What the profile says
- What the recommendation says
- What taste does to it
- What got blocked
- The brief
- The manifest
- What to take from this

## The source

An SVG of a seed with two leaves and a live-text wordmark. Three named parts: `seed`, `leaf-left`, `leaf-right`. Single-colour fill, no stroke, no gradient, no mask.

Live text matters before anything else does, because it gates three families at once.

## What the profile says

```text
kind                 svg
component_count      3
named_parts          ["seed", "leaf-left", "leaf-right"]
complexity           17.6   band: atomic
hole_count           0
sym_mirror           0.051
stroke_present       false
fill_present         true
text_present         true
text_outlined        false
color_count          2
palette              [{"hex": "#0066cc", "hits": 5}, {"hex": "#000000", "hits": 1}]
capability rung      7   unlocks: variable-axis typography, text on a path
```

Three readings matter more than the rest.

The rung is 7 on the strength of one live text node, not on the strength of the artwork. Rung 7 outranks gradient and mask support because live text unlocks the most, and because `text_outlined` is false the glyphs are renderer-dependent rather than baked. That single fact drives every block below.

`sym_mirror` of 0.051 is ambiguous, so the profiler halves symmetry-derived evidence and says so in the notes. Take the warning rather than reading the mark as asymmetric by eye.

The palette is `#0066cc` at five declared occurrences and `#000000` at one. On a vector source this counts declared paints, not covered area, so it is a list of the brand's colours rather than a dominant-colour analysis. It is still the value to test against; delivery files that ask for a check on the brand colour mean this, not a colour estimated by eye.

## What the recommendation says

```text
primary      mask_wipe            0.35   WORD-02
supporting   separation_explode   0.40   SEP-01
supporting   separation_ordered   0.35   SEP-04
confidence   inferred
```

Read that top line again. The primary scores lower than the first supporting entry. That is not an error and it is not a sort bug; it is the taste gate landing one step later, and it is the single most important thing in this file.

## What taste does to it

Adding `--register premium --frequency occasional` produces:

```text
budget     duration_ceiling_s 0.96   gesture_ceiling 1   overshoot_ceiling 0.0
permitted  ["mask_wipe", "separation_ordered"]
vetoed     separation_explode (SEP-01, score 0.40)
             "the claim is that everything unnecessary was removed; a second
              gesture or an effect contradicts it"  [register: premium]
cliches    mask_wipe
             "a wipe always works, so it is always used"
             replacement: a wipe whose axis derives from the mark's geometry
             verdict: acceptable only with a stated brand referent and in a
                      register that licenses it
notes      register-preferred and permitted: mask_wipe
           a vetoed technique must be dropped from the ranking, not demoted;
           record the register as the reason in the brief
```

`separation_explode` had the highest raw score and is now gone. It was dropped, not demoted: it does not appear as a lower-ranked supporting option, because a vetoed technique that stays in the list will be picked up again on the next pass.

`mask_wipe` becomes primary because it is both permitted and register-preferred. Its own cliche warning fired, and the verdict is conditional rather than disqualifying: a wipe needs a stated brand referent. This mark is a seed opening, so the wipe axis should derive from that geometry rather than sweep left to right, and the referent goes in the brief.

The budget is the hard ceiling for everything downstream: **0.96 s**, one gesture, zero overshoot. Premium does not licence overshoot at any frequency.

## What got blocked

```text
kinetic_typography    LIVE_TEXT   1 live text node(s); renderer-dependent glyphs break per-path timing
line_draw_on          LIVE_TEXT   1 live text node(s); renderer-dependent glyphs break per-path timing
multi_stroke_trace    LIVE_TEXT   1 live text node(s); renderer-dependent glyphs break per-path timing
```

Three families are unavailable for a reason that has nothing to do with taste. Remedy is to outline the text, which converts this into a different source at a different rung and requires re-profiling rather than a local edit.

The draw plan reported by `--draw-plan` is worth reading even though line drawing is blocked, because it shows the tool's judgement:

```text
euler            circuit: the mark can be drawn from any point without lifting the pen
odd_vertex_count 0
pen_lifts_required 0
subpath_count    3
start_point_rule prefer a free degree-one endpoint; then 12 o'clock clockwise for a
                 closed mark; then reading direction. Never start at a junction.
symmetry_warning if the mark is mirror-symmetric and closed, do not start on the axis
                 of symmetry; it leaves a visible seam.
```

Zero pen lifts means a single continuous stroke would work if the source were outlined. The symmetry warning is what the ambiguous `sym_mirror` costs: start off-axis or accept a seam.

## The brief

Carry forward only what the tools decided, and label anything inferred:

| Field | Value | Origin |
|---|---|---|
| `primary_concept` | WORD-02 mask wipe | measured, then permitted by the register |
| `why_it_fits` | The seed parts along its own axis; the wipe derives from that geometry | **inferred** — this is the brand referent the cliche verdict demanded |
| `duration` | ≤ 0.96 s | taste budget, `premium` × `occasional` |
| `gesture_count` | 1 | taste budget |
| `overshoot` | 0.0 | taste budget |
| `layer_inventory` | `seed`, `leaf-left`, `leaf-right` | observed from `named_parts` |
| `dropped_technique` | `separation_explode` | register veto, premium |
| `blocking_reason` | live text not outlined | gate code `LIVE_TEXT` |

The `why_it_fits` line is the one to watch. Nothing measured it; it is an inference, and `references/intake-and-planning.md` requires that inferred values are recorded as such rather than treated as approvals.

## The manifest

The manifest carries the technique in its own channel, the layer geometry from the source, and the environment it was produced in. Two blocks are worth naming because they are what the validator will refuse to accept without:

- `detection` with the `register`, `frequency`, and the `taste` budget, so the primary can be checked against the veto it passed.
- `environment` with the probe date, the mode verdict, and the capability states, so a later render can be shown to match the approved one.

Validate before rendering:

```bash
python scripts/validate_motion_spec.py path/to/motion-spec.json --check-files
```

## What to take from this

1. **The raw ranking is not the answer.** The highest-scoring technique was vetoed. Read the taste block, not the score order.
2. **A veto removes, it does not demote.** A technique that stays in a list gets picked up again.
3. **One gate code can close three families.** Live text blocked kinetic typography, line drawing, and multi-stroke trace together, and the remedy is a source change rather than a preference.
4. **Budgets are ceilings, not suggestions.** 0.96 s and zero overshoot govern every value downstream.
5. **A cliche warning asks for a referent, not a different technique.** The wipe survived because the mark gives it a reason.
6. **Say what was inferred.** The brand referent in the brief is an inference and is labelled one.
