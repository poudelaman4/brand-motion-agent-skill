# Matter and Particle Effects

Budget every technique here as an accent, never as the reveal itself.

## Contents

- Source requirement
- Determinism and budget
- Scenario blocks
- Filter parameters
- Alpha delivery
- Forbidden here
- Failure modes
- QA

## Source requirement

Matter effects are the one advanced family that works on a flattened raster; confirm the source first.

| Technique | Requires |
|---|---|
| FX-01 Particle assemble | Silhouette |
| FX-02 Alpha-threshold dissolve | Alpha channel |
| FX-03 Turbulence displacement | Filter runtime |
| FX-04 Halftone and dot-matrix build | Grid, threshold |
| FX-05 Glitch and RGB split | 3 channel copies |

Record that none produce semantic layers; keep particles from implying absent layers.

## Determinism and budget

Accept a particle system only when it is fully deterministic: derive every position, lifetime, size, and phase as a pure function of frame number and a stable seed, so a frame-driven renderer produces identical output across parallel frame renders.

```text
index     int 0..N-1
seed key  string  `logo-seed-${index}`
origin    px, px  sampled silhouette
angle     deg      seeded 0–360 deg
speed     px/frame seeded 0.2–1.2
lifetime  frames    seeded 12–40
size      px        seeded 1–6
spin      deg/frame seeded ±0.4
```

| Cap | Value |
|---|---|
| Particle count | 60–120 per one-shot reveal |
| Bursts | 1 |
| Lifetime | normally under 40 frames |
| Added duration | should not push past 2.5 s |

Mark runtime randomness `blocked` in a frame-driven renderer. Replace `Math.random()`, timestamps, module counters, and CSS transitions with a seeded generator on a stable string, normally `random('logo-seed-<index>')`. Treat 60–120 as `provisional`; hero morphs run far higher, `observed`.

## Scenario blocks

### FX-01 — Particle assemble

**Intent:** express convergence, not construction.
**Layers:** sampled mark, sprite layer.
**Motion:** emit outward, converge.
**Timing:** 1.2–2.0 s; 500–700 ms hold.
**Easing:** `enter` travel, linear spin.
**Anchors:** sampled points, centroid.
**Risks:** hollow interior, count mismatch.

### FX-02 — Alpha-threshold dissolve

**Intent:** disintegrate, then resolve exactly.
**Layers:** one mark, one noise field.
**Motion:** sweep a threshold over alpha.
**Timing:** 0.8–1.5 s, sweep under 1.2 s.
**Easing:** linear threshold, `enter` resolve.
**Anchors:** none; sweep direction only.
**Risks:** static, whole-mark blink, `linearRGB` shift.

### FX-03 — Turbulence displacement

**Intent:** agitate the surface, stay solid.
**Layers:** one group, never per path.
**Motion:** displace, return scale to 0.
**Timing:** 0.6–1.2 s; peak at the beat.
**Easing:** symmetric out-and-back.
**Anchors:** group bounding box, filter region.
**Risks:** clipped region, non-zero end scale.

### FX-04 — Halftone and dot-matrix build

**Intent:** express data, order, or construction.
**Layers:** one silhouette, one generated grid.
**Motion:** grow or drop dots in one order.
**Timing:** 1.0–2.0 s, grid stagger.
**Easing:** `enter` per dot.
**Anchors:** grid origin on the bounding box.
**Risks:** texture, not a mark; uneven margins.

### FX-05 — Glitch and RGB split

**Intent:** punctuate a readable mark.
**Layers:** 3 copies, one per channel.
**Motion:** offset 2–6 px on x, step, return 0.
**Timing:** 0.4–0.9 s; punctuation, not a reveal.
**Easing:** `steps()` stutter only.
**Anchors:** mark position, copies at 0.
**Risks:** over roughly 700 ms, `screen` identity on white.

## Filter parameters

Hold turbulence `baseFrequency` normally in the 0.01–0.05 band in user units, with 2–4 octaves. Read higher as television static, lower as a whole-mark blink. Scale to the viewBox.

Apply the alpha-threshold dissolve as a threshold on the logo's own alpha, swept by a spatial noise field, so it needs no layer data.

```svg
<filter id="dissolve" x="-10%" y="-10%" width="120%" height="120%"
        color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed="7"/>
  <feColorMatrix type="saturate" values="0"/>
  <feComponentTransfer result="t">
    <feFuncA type="linear" slope="1" intercept="0"/>
  </feComponentTransfer>
  <feComposite in="SourceGraphic" in2="t" operator="in"/>
</filter>
```

Animate the transfer slope, not the seed. Order the chain turbulence, matrix, transfer, composite. Set explicit `x/y/width/height`; defaults clip.

## Alpha delivery

Route additive and screen-blend highlights, and any soft-edged particle layer, through a matte-aware path or a higher-bit-depth intermediate; they band badly in 8-bit `yuva420p` alpha video. Keep particles out of the alpha master without a matte, and inspect the poster frame for residue.

## Forbidden here

Reject this family wherever it is already forbidden: `contexts/premium-and-minimal.md`, `contexts/wellness-and-organic.md`, `contexts/education-and-lms.md`. Reject it for any identity-critical mark where texture competes with geometry. Permit at most one small burst in a playful brand, only after the mark reads, per `contexts/playful-and-character.md`. Mark particles combined with glitch, 3D, and a camera move `BLOCKED`.

## Failure modes

**Non-determinism between renders.** Seed on a stable string, then diff.

**Particles obscuring the silhouette.** Cut count and lifetime; match the final frame.

**Banding in the alpha master.** Move soft particles to a matte-aware or higher-bit-depth path.

**A dissolve that reads as television static.** Drop `baseFrequency` into the 0.01–0.05 band, octaves to 2–3.

**A mark turning into texture.** Lower the dot count; recognizability outranks density.

## QA

- Re-render the same frame range twice; confirm identical output.
- Sample silhouette alpha; confirm a solid interior.
- Check the poster and final hold for particle residue.
- Probe the encoded alpha file; inspect on checkerboard and solid color.
- Confirm the final frame matches the master at 32, 64, 128 px.

Frequency bands are `observed`; the particle budget is `provisional` pending per-brand measurement.
