# Generative Video and Brand Motion

Generative video may produce everything except the approved identity. This file makes that line operable: what a model is for, what fails, how to composite a generated plate under approved geometry, and what must be recorded so the asset is reproducible.

## Contents

- The line
- What a model is for
- What fails
- The composite handoff
- Control mechanisms
- Determinism and reproducibility
- Licensing and cost
- When not to use it at all
- Failure modes
- QA

## The line

A generative video model may produce atmosphere, environment, texture, b-roll, and footage the brand did not have. It may not produce the mark, the wordmark, the monogram, the lockup, or any part of the approved identity.

Treat all of the following as identity, and keep them out of every generated region:

- The mark, in any colour, weight, or stylisation
- The wordmark, including single letters and partial letterforms
- The monogram and any interlocked or ligatured initials
- The lockup and its fixed spatial relationships
- The distinctive geometry of a protected or registered mark
- Anything a reasonable viewer would identify as the brand

A model asked to draw a logo produces something adjacent to it. Adjacent is a failure, not a near-miss: it is unusable for delivery, and it is a liability if it resembles a third party's protected mark. This is why the prohibition is absolute rather than a quality preference.

The exception is atmosphere. A generated plate containing no identity content is a legitimate asset, and the composite built from it can be indistinguishable from one shot conventionally.

## What a model is for

| Purpose | Typical duration | Generate | Constraint |
|---|---|---|---|
| Environment plate | 1–4 s | Abstract gradient field, fog, particulate haze, distant light | No geometry a viewer could read as a mark |
| Texture source | still or loop | Grain, paper fibre, brushed metal, dust | Must tile or loop seamlessly; check the seam |
| Light source material | 1–3 s | A soft moving highlight, flare, or glow plate | Composite under the mark with an additive blend, never over it |
| B-roll | 2–6 s | Abstract motion the brand could not otherwise afford | No recognisable object, place, or person without clearance |
| Particle field | 1–3 s | A point or sprite field to seed a deterministic particle layer | Bake to a deterministic source; never leave it stochastic |

Keep the generated asset's role describable in one sentence that contains no brand noun. "A soft grey particulate haze plate for the lower third" is describable. "A logo reveal" is not, and the sentence failing is the signal to stop.

## What fails

| Failure | Symptom | Why | Controlled by |
|---|---|---|---|
| Letterform mutation | A letter becomes a different letter partway through | The model renders plausible letter-like shapes, not glyphs | Nothing reliable. Never delegate letterforms |
| Counter filling | The hole in an O, A, B, or R closes under motion | Counters are the lowest-salience feature and get averaged | Nothing reliable |
| Stroke weight drift | A stroke thickens or thins across frames | Weight is a global average the model re-samples per frame | Seed and reference conditioning reduce but do not remove it |
| Colour drift | The brand colour shifts hue or saturation over the shot | Colour is not pinned by a text prompt | Reference-image conditioning; a colour-check frame gate |
| Geometry drift | The mark is subtly different at frame 60 than at frame 1 | No per-frame constraint on shape | First and last frame conditioning, then a geometry diff |
| Temporal flicker | Whole regions shimmer or pulse | The model re-samples detail per frame | Frame-to-frame difference check; a longer shot is worse, not better |
| Non-determinism | The same prompt and seed return a different result | Vendor models change, and seeds are not stable across versions | Record the model version; a re-render is a new asset |
| Resemblance to a third party | The output resembles a protected mark | The training distribution contains famous marks | Nothing automatic. Review every frame |
| Outright refusal | The provider declines the request | Most providers refuse well-known brand logos `[UNVERIFIED]` | Expected. Do not attempt to evade a refusal |

The first two rows are the reason the line exists. They are not edge cases that better prompting solves; they are the defining behaviour of a model that has learned what marks *look like* rather than what any specific mark *is*.

## The composite handoff

This is the procedure that makes constrained use work. The model produces a plate with no identity in it, and approved geometry is composited above it.

1. **Define the plate region.** State the area the model will fill and confirm the mark's bounding box does not intersect it, including under every crop the delivery matrix requires.
2. **Generate the plate.** Record the model family, the model version, the full prompt, the seed, the aspect ratio, the duration, and the frame rate.
3. **Inspect for accidental identity.** Review every frame, not the first and last. Look for letterforms, mark-like geometry, and resemblance to a third party. Reject the plate on any hit; do not crop around it.
4. **Mask or key it.** Produce an alpha channel, and check the edges on both a light and a dark background. A keyed plate with a dark fringe reads as a defect.
5. **Composite the approved geometry above it.** The mark, wordmark, and lockup come from the approved source, never from the plate. For an additive highlight, mask the plate to the mark's silhouette so the light cannot spill onto the background.
6. **Verify the final state.** Run the normal final-frame comparison against the reference. This checks the composite, which is what ships.
7. **Record the plate as a third-party asset.** Model, version, prompt, seed, licence, and generation date all belong in the delivery notes alongside the source and the manifest.

Step 3 is the one that gets skipped and the one that cannot be. Step 7 is what makes the asset reproducible; a plate with no seed is not a deliverable, it is a coincidence.

## Control mechanisms

Describe controls by category rather than by product, because the product names and their behaviour change faster than the categories do. All product-specific claims are `[UNVERIFIED]`.

| Category | Improves | Does not improve |
|---|---|---|
| Seed control | Reproducibility within one model version | Anything across a version change |
| Reference-image conditioning | Overall form, palette, and composition | Per-frame identity of a specific mark |
| First and last frame conditioning | The two endpoints and therefore the arc between them | Identity at the intermediate frames |
| Subject or character consistency | A recurring subject across shots `[UNVERIFIED]` | Letterform or counter fidelity |
| Motion brush or keyframe control | Where the motion happens | The identity of what is moving |
| Mask and rotoscope input | Which region the model may alter | Content outside the mask, and identity inside it |
| Regional editing | Iterating one area without regenerating all | Global colour and weight drift |
| Negative prompting | Suppressing some categories of artefact `[UNVERIFIED]` | Determinism; it is a sampling bias, not a constraint |

None of these is a substitute for compositing approved geometry. The correct mental model is that a control reduces how far a plate strays, and compositing is what guarantees the identity.

## Determinism and reproducibility

A non-reproducible asset cannot be a deliverable, because nobody can prove the shipped file is the approved file.

- Record the model family, the model version, the seed, and the prompt as part of the asset record, next to the licence.
- Treat a silent vendor model update as invalidating every prior render from that model. A re-release is not a re-export.
- Re-render and compare before any re-release, using the same comparison tooling as the final-state check.
- Never regenerate a plate to "improve" it after approval. That is a new asset and it needs a new approval.
- Prefer a plate that is static or short. The shorter the generation, the fewer frames can drift, and a still has no drift at all.

## Licensing and cost

Terms differ per provider, per plan tier, and per region, and they change often. Verify current terms for the specific provider and tier before commercial delivery. This file is not legal advice and states no terms.

What is worth checking:

- Whether commercial use is included at the plan tier being used, and whether the output carries any attribution requirement
- Whether the provider's terms grant rights over the output or only a licence to use it
- Whether indemnity, exclusivity, or a right-of-clarification exists for generated output in a commercial context
- Whether the brand's own guidelines prohibit third-party generated assets in its identity, which many enterprise brands do

Cost characteristics that affect scheduling:

- Generation is per-attempt and the attempt count needed for a usable plate is unpredictable, typically several
- Each attempt costs wall-clock time far exceeding a conventional render of the same plate
- Iterating a plate to correct a drift is more expensive than generating a longer, simpler plate and grading it conventionally
- Once composited, the plate is usually reusable across the delivery matrix, which is where its cost amortises

Compare against the alternative honestly. If a plate needs more than a handful of attempts, shooting it or rendering it conventionally is usually cheaper and always reproducible.

## When not to use it at all

- The deliverable **is** the mark, the wordmark, or the lockup
- The brand has a published no-substitution or no-generated-asset rule
- The timeline cannot absorb an unpredictable iteration count
- The client has not approved a third-party generated asset inside the identity
- The plate would need so much correction that rendering or shooting it is cheaper
- The identity is a protected or registered mark, where resemblance risk is not acceptable at any quality
- The output is destined for a context where provenance must be provable, such as a regulatory or legal deliverable

## Failure modes

**Symptom:** the mark drifts subtly across the shot and every individual frame passes review. **Repair:** run a frame-to-frame geometry comparison of the composited mark, not a visual scan. Sub-pixel drift is invisible frame to frame and obvious as a difference.

**Symptom:** a plate contains a shape a viewer reads as a mark, and it ships because nobody watched the whole clip. **Repair:** review every frame, not the endpoints. Reject on any hit rather than cropping around it.

**Symptom:** a re-release produces a visibly different plate. **Repair:** the model version changed. Treat the new render as a new asset requiring approval, and pin the model version in the asset record.

**Symptom:** an additive highlight over the mark fringes against a light background. **Repair:** mask the plate to the mark's silhouette and check on both a light and a dark background; a masked plate should have no visible edge at all.

## QA

- [ ] The plate region does not intersect the mark's bounding box in any crop in the delivery matrix
- [ ] Every frame of the plate was reviewed for accidental identity content and for resemblance to a third-party mark
- [ ] The mark, wordmark, and lockup are composited from the approved source, not from the plate
- [ ] A frame-to-frame geometry comparison of the composited mark passes, not only a first and last frame check
- [ ] The model family, version, prompt, and seed are recorded in the delivery notes
- [ ] The plate is keyed and checked on both a light and a dark background

A model is a plate source, not an identity source. That is the whole file.
