# Motion System and Handoff

Turn one approved animation into a system that generates every later asset, not a document that describes one already made.

## Contents

- One master many variants
- The motion system
- Token layer
- Component handoff
- Versioning and ownership
- Governance and the review matrix
- Constraints
- Failure modes
- QA

## One master, many variants

Define one canonical motion specification with a single timing model, then derive every composition from it. The manifest at `qa/motion-manifest.md` is that definition; the square, vertical, horizontal, alpha, white, dark, and interactive compositions are recompositions of it, each with its own canvas and safe-area check. Regenerate a variant and it inherits the timing. Rebuild one from scratch and the brand ends up moving like a committee.

| Variant | Canvas | What changes | What must not change |
|---|---|---|---|
| Square master | 1080×1080 px | Nothing; this is the canonical definition | Frame rate, duration, settle frame, layer order |
| Vertical | 1080×1920 px | Layout, safe area, clear space | Timing model, easing tokens, gesture vocabulary |
| Horizontal | 1920×1080 px | Layout and lockup proportions | Timing model, overshoot ceiling, final state |
| Alpha master | Transparent, canonical canvas | Background only | Colour values, shadow treatment, timing |
| White matte | Canonical canvas on `#FFFFFF` | The matte | A matte baked into the alpha master |
| Dark or brand ground | Canonical canvas | Background prop or separate composition | Approved logo colour values |
| Interactive | Runtime canvas per breakpoint | Named states, quality setting, playback control | Final state, reduced-motion branch, curve tokens |

## The motion system

Hold ten layers and enforce each inside a tool: a rule no template, preset, or exported token file carries is documentation, not a system.

| Layer | What it fixes | Canonical value |
|---|---|---|
| Easing curves | Curve shape and overshoot per gesture | 7 published tokens in `assets/motion-tokens.json` |
| Durations | Length by purpose and by frequency | 1.2–4.0 s one-shot; 3.0–8.0 s loop; 90–180 ms UI |
| Stagger rule | Offset between related groups | 40–80 ms meaningful groups; 20–50 ms dense wordmark |
| Overshoot ceiling | Maximum overshoot by register | 0.0% identity-critical; 5% organic; 8% playful |
| Loop rules | Seam, dwell, return leg | First and last frame share a state; return leg mirrors outbound |
| Minimum sizes | Legibility floor per surface | 40×40 px app icon; 0.275 in emblem; 0.65 in wordmark |
| Safe areas | Exclusion box per context | 90% title box for broadcast, captions |
| Prohibited effects | Techniques the brand never ships | Particles, glow, chromatic aberration, strobe |
| Format requirements | Container, codec, file ceiling per platform | H.264 MP4 opaque; WebM VP9 for web alpha |
| Reduced-motion asset | A designed static frame, not a paused video | Required on every variant, not only the master |

Export the tokens as CSS custom properties, JSON design tokens, Figma variables, or a platform token set, and expose a control only where a token exists. Read `taste/fit-decisions.md` for what a guideline must constrain.

## Token layer

Publish curves as numeric values rather than names, so no implementer has to guess what `settle` means. Scale a duration with travel distance measured in logo widths and with the rendered area being moved. Keep exits shorter than entrances, and accelerating relative to them.

```json
{
  "name": "one_shot.entrance.settle",
  "curve": [0.2, 0.0, 0.0, 1.0],
  "duration_ms": [1200, 4000],
  "duration_model": "scales with travel distance and rendered mark height",
  "valid_in": ["one_shot_reveal", "page_load_hero", "ident"],
  "register": ["premium_minimal", "corporate_institutional"],
  "overshoot_max": 0.0,
  "exit_pair": "one_shot.exit.accelerate"
}
```

## Component handoff

Hand over a set, not a file. A handoff without reproduction commands is not a handoff; a manifest that cannot be validated is documentation.

| Artefact | What it must contain |
|---|---|
| Canonical manifest | Intervals and frame order that pass `scripts/validate_motion_spec.py` unedited |
| Source project | Layered and editable, at the canonical frame rate and artboard |
| Rendered master and variants | Every row of the delivery matrix, named by canvas and background |
| Static poster | The final frame decoded from the encoded file, not a still |
| Checkpoint evidence | Contact sheet at the timeline frames, per `qa/review-matrix.md` |
| Reduced-motion variant | A designed static frame plus the host-side branch that selects it |
| Still frames | 16 px, 32 px, 64 px, 128 px, and the real delivery size |
| Reproduction commands | Exact render and validation commands with dependency versions |
| Known limitations | Unsupported effects and platform gaps, as `WARN` or `BLOCKED` |

## Versioning and ownership

Version a motion system with the identity it belongs to, under semantic versioning plus a variant matrix per platform and frame-rate standard; a rebrand is not one event, and the bug, the endpage, and the toolkit version separately. Treat a token change as a change to every asset derived from it, and regenerate on the same ticket. Name an owner and set a review cadence; an unowned guideline decays into a PDF nobody diffs.

## Governance and the review matrix

| Decision | Evidence required |
|---|---|
| Concept | One named concept from `taxonomy.md` and the referent it claims |
| Register | A quoted brand claim checked against the register row |
| Primary gesture | Settle and poster frames at the real delivery size |
| Duration | A measured play time inside the token band |
| Delivery matrix | One conformed row per platform, probed after encoding |
| Reduced-motion asset | A captured run with reduce motion enabled |
| Departure from a published guideline | The reason, the approver, and the date |

Record a departure as a decision with both sides named; ship it silently and it returns on the next revision.

## Constraints

| Constraint | Rule |
|---|---|
| Maximum one-shot duration | ≤4.0 s, normally 1.2–4.0 s |
| Minimum legible mark size | 40×40 px on an app surface; 0.275 in emblem, 0.65 in wordmark in print |
| Minimum readable wordmark duration | 500–1000 ms resolved hold, readable within 1 s of first appearance |
| Loop seam rule | First and last frame share one state; the return leg mirrors the outbound |
| Alpha master rule | Transparent, no baked matte, no recoloured mark, one timing model across backgrounds |
| Reduced-motion obligation | Ship a designed static frame and replace translation with a fade, never with speed |

## Failure modes

**Token change with no regeneration**

**Symptom:** change the settle curve in the token file, ship one re-render, and leave 12 derived assets on the old value.

**Repair:** treat a token edit as a breaking change, list every asset derived from it, and re-render the set at once.

**Rules the tools do not enforce**

**Symptom:** publish a stagger rule while component code keeps free-floating durations, then find the mark moving differently in 11 places.

**Repair:** export the rules as tokens, and remove any control the token layer does not cover.

**A committee of logos**

**Symptom:** hand-author a vertical cutdown and a dark-ground version, then find neither shares the master's frame order.

**Repair:** derive every variant from the manifest and diff the timing model before review.

**Reduced motion that only shortens**

**Symptom:** set every duration to 0.01 ms, lose the feedback that signals state change, and leave a script-driven player running.

**Repair:** select a designed static frame host-side, and make the reduced path a designed asset, not a faster one.

## QA

- Re-derive every variant from the canonical manifest and diff the timing model; reject anything re-animated by hand.
- Change one token, re-render one asset, and confirm every other asset fails conformance until regenerated.
- Load the exported token file into the tool the team actually uses and confirm it resolves unedited.
- Run `scripts/validate_motion_spec.py` against every manifest in the system, not only the master.
- Confirm each review-matrix row carries a named owner and a date, and that no departure lives only in a comment.

Token coverage across delivered systems is `inferred` and observed only in published guidelines, so hold the layer list as `provisional`.
