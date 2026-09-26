# Camera and Perspective as Craft

A camera move is a claim that a world exists around the mark. Most logo reveals that use one are using it as a transition, and are better served by a cut.

## Contents

- When there is a camera
- The moves
- Projection
- Framing rules
- Scale versus depth
- Limits
- Failure modes
- QA

## When there is a camera

Name the world before naming a move: what the camera looks at past the mark, what the mark stands on, what occludes it from behind. A mark on a page is a sticker on a plane — no floor, no horizon, no second object — so a push-in is a scale change pretending to be depth, the same claim a shadow makes with no catcher, per `craft/light-and-shadow.md`.

**Governing rule:** permit a camera only when the mark is the thing the viewer moves past, not the thing inspected. A mark arriving from beyond frame, passing, and settling earns one; a mark that grows, sharpens, or turns on a stage does not.

Cut instead whenever the intent is only to change size, position, focus, or angle. Read `taste/cliche-and-restraint.md` before adding a second move.

## The moves

Treat every entry as a claim first and a technique second; read timing in `motion-foundations.md` and renderer mechanics in `implementation/advanced-mechanics.md`.

| Move | What it is in 2D | Real property names | Cost | Good for | Trap |
|---|---|---|---:|---|---|
| Dolly or zoom | Uniform scale | `scale()`; `perspective` + `translateZ()` | 0 layers | An opening push | Identical to a zoom on one plane; a dolly is a scale with a claim |
| Truck or pedestal | A pan | `translateX`/`translateY` × depth | 3+ layers | A stage across a lockup | One layer trucked is a pan; two is a slide |
| Parallax push | Differential motion | `translate3d` per layer | 3+ layers | Seating a mark in a world | Under three planes it reads as jitter |
| Orbit | Rotation | `rotateX`/`rotateY` | 1 transform | One turn of a 3D mark | A flat mark has no side; the orbit shows the back is the front |
| Depth of field | Blur by distance from focus | `filter: blur()`; Focus Distance | 1 filter/frame | One rack focus, once | Blur past 8 px reads as a bad image, not depth |
| Lens distortion | Radial warp | Brown–Conrady `k₁`; canvas, not SVG | Renderer | A 2–4 frame entrance tell | `k` under 0.05 is invisible, over 0.4 a fisheye gag |
| Perspective tilt | Fixed-axis shear | `rotateX`/`rotateY` off `perspective-origin` | 1 transform | A ≤15° reveal of a plate | Off-centre origin reads as a hinge; past 15° the silhouette breaks |
| Settle move | Overshoot then resolve | `settle` token keyframes | 1 track | Final lockup assembly, once | 3–8% overshoot; one is a bounce, two decaying is a settle |
| Camera shake | Decaying high-frequency noise | summed sines | 1 transform | A 150–300 ms impact transient | 1–4 px at 1080p; a loop is a gimmick and a trigger |

## Projection

Derive the projection before the transform, then hold it.

```text
true isometric            sx = (x − z) · cos 30° = (x − z) · 0.86603
                          sy = ((x + z) · sin 30°) − y = (x + z) · 0.5 − y
                          three axes 120° apart, ground axes at ±30°

2:1 dimetric              ground angle arctan(1/2) = 26.5651°
                          axis separations 116.565°, 116.565°, 126.870°

foreshortening            cube tilt  arctan(1/√2) = 35.2644°
                          projection scale  cos 35.2644° = √(2/3) = 0.81650
                          un-foreshorten     √(3/2) = 1.22474
                          CSS back tip  90° − 35.2644° = 54.7356°

lens distance             600–1200 px long lens · below 400 px wide-angle
```

Accept 2:1 dimetric as the usual case; nearly all product and game work is dimetric, and true-30° transforms on a 2:1 lockup make its edges stop meeting.

State the flat-mark limit plainly: a mark drawn flat has no back, so extruding it yields a solid slab, and an orbit only discloses it.

Apply the consistency rule without exception. `perspective-origin` is the vanishing point, and a page carrying 3D already has one. Agree within ≤2° or the mark reads as pasted on, and no shading repairs it.

## Framing rules

Hold the composition. Animate the logo inside a fixed artboard and camera origin; move the mark, not the crop.

1. Set perspective distance at 600–1200 px. Below 400 px bends straight edges; above 1500 px it is indistinguishable from `scale()`.
2. Leave clear space unmoved and the final lockup unrefined; diff the last frame against the master within 1/255 per channel.
3. Recompose per aspect ratio, never crop. 16:9, 1:1, 4:5, and 9:16 each need their own check; a centre crop takes descenders.
4. Budget total differential across layers at ≤4–6% of frame width `[house range]`. A logo has no subject depth, so any perceptible parallax is stylisation and should stay under the threshold for a mistake.

## Scale versus depth

Separate the two before committing. Hold the outline constant and ask whether the relationship between parts changed. Uniform change is scale; any differential is depth, and depth claims a world.

The distinction decides whether the mark may shrink at all. An approved size is a brand rule, so a scale animation moves a brand value, while a depth animation leaves the final size exact and only claims the mark was further away.

Set the entry scale deliberately. Starting at zero reads as an object appearing from nothing, asserting a world and a physical size a symbol lacks. Starting high, at 1.04–1.08×, reads as something always present, slightly further away; that is the depth read. A start of 0.88–0.97× is the accepted size-constancy step, per `craft/depth-and-material.md`.

## Limits

- Do not add a camera to a flat brand identity; flatness is the product.
- Do not add a camera to a small square deliverable, normally 108–512 px, where there is nowhere to move through.
- Do not add a camera to a mark that must read at notification size.
- Do not add a parallax push to a source with no separable depth planes.
- Do not add a move that pushes the sequence past the pacing ceiling, normally ≤2.5 s (`taste/quality-tests.md`).
- Honour `prefers-reduced-motion` always; shake and orbit are triggers, not preferences.

## Failure modes

- **Symptom:** the mark reads as pasted onto the page, turned independently of everything near it. **Repair:** match `perspective-origin` to the page's vanishing point within ≤2°, or drop the tilt.
- **Symptom:** a parallax push reads as jitter. **Repair:** the source had only two planes. Add a third, or cut the move.
- **Symptom:** the dolly is a zoom. **Repair:** one layer cannot show depth; give a second its own `translateZ()`, or settle instead.
- **Symptom:** an orbit exposes reversed lettering. **Repair:** set `backface-visibility: hidden`, or accept that a flat mark has no back to turn.
- **Symptom:** the lockup lands off-frame or clipped. **Repair:** restore the fixed artboard and recompose per aspect ratio.

## QA

- Play the reveal on a surface carrying other 3D elements; confirm vanishing points agree within ≤2°, or that no tilt was used.
- Play it at 24–48 px and the 108 px square; confirm the move is absent or harmless.
- Measure differential across layers; keep the total at or below 4–6% of frame width.
- Diff the final frame against the master within 1/255 per channel for position, scale, and clear space.
- Check all four canvas edges and each aspect ratio for a cropped mark.
- Add a `filter`, `opacity` below 1, or a `clip-path` inside the 3D context; confirm the subtree has not force-flattened, per `implementation/advanced-mechanics.md`.

The move taxonomy is `observed`, the projection constants exact, the percentage and amplitude ranges house conventions; treat them as `provisional` until measured on the delivered renderer.
