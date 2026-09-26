# Light and Shadow as Craft

Shadow and light are the cheapest depth cues available and the most abused. Apply both as a volume claim that flat geometry must earn.

## Contents

- What light does
- Shadow species
- Shadow parameters
- Surface and contact
- Lighting a flat mark
- Rim and edge light
- Shadow in the alpha master
- Limits
- Failure modes
- QA

## What light does

Apply to any technique — a line draw, a separation, a mask wipe, a kinetic-type reveal, product shot. Read timing in `motion-foundations.md`.

Treat a mark's identity as its flat geometry. A shadow asserts a second surface: a decision, not a pass.

**Governing rule:** every shadow is a relationship between two surfaces. A transparent master has no second surface.

- Do not ship a master with a shadow baked in; ship flat plus a documented recipe.

## Shadow species

| Species | Communicates | Blur σ | Offset | Opacity | Fits | Kills |
|---|---|---:|---:|---:|---|---|
| Hard / flat | Sticker | 0% | 1–3% | 25–45% | Known surface | Volume claims |
| Soft / ambient | Proximity | 4–9% | 0–1% | 12–20% | Any mark, as base | Alone; fog |
| Contact / occlusion | Weight | 0.5–2% | dy 0.25–0.75% | 20–35% | Plate, card, footer | Unknown ground |
| Cast / key | Azimuth | 2–5% | dx:dy, one azimuth | 30–50% | Exploded lockup | Non-planar marks |
| Long-angle | Time of day | 8–20% | dy 1.5–3× height | 15–25% | Photo stage | Avatars; crops |

% of mark = bounding-box smaller dimension.

**Limits:** permit two shadows at most — ambient plus cast — and two elevation states per loop. Fewer levels carry more meaning; a third reads as a stack.

## Shadow parameters

```text
σ        0.5–9% of mark smaller dim     SVG blur unit
offset   0.25–3% of mark smaller dim   dx:dy on one azimuth
peak     0.12–0.50 opacity             weight, not darkness
flood    hsl(215–235, 20–35%, 4–10%)   tinted near-black, never #000
region   x/y -30%, w/h 160%            default -10% / 120% clips a large blur
```

```svg
<filter id="stack" x="-30%" y="-30%" width="160%" height="170%"
        color-interpolation-filters="sRGB">
  <feGaussianBlur in="SourceAlpha" stdDeviation="9" result="aBlur"/>
  <feOffset in="aBlur" dx="0" dy="3" result="aOff"/>
  <feFlood flood-color="#22304a" flood-opacity="0.20" result="aFlood"/>
  <feComposite in="aFlood" in2="aOff" operator="in" result="ambient"/>
  <feGaussianBlur in="SourceAlpha" stdDeviation="2.5" result="kBlur"/>
  <feOffset in="kBlur" dx="3" dy="5" result="kOff"/>
  <feFlood flood-color="#05070d" flood-opacity="0.45" result="kFlood"/>
  <feComposite in="kFlood" in2="kOff" operator="in" result="cast"/>
  <feMerge>
    <feMergeNode in="ambient"/><feMergeNode in="cast"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

- Put `color-interpolation-filters="sRGB"` on every brand-asset filter; `linearRGB` reads wider and darker than the tool numbers it replaces.
- Halve any imported blur: `stdDeviation` and `drop-shadow()` take a standard deviation, a tool's number is a radius, and the 2× factor is de-facto, `[UNVERIFIED]` as normative.
- Use `drop-shadow()` for a mark, `box-shadow` never, except a literal rectangle: `box-shadow` follows the element box, not the alpha.
- Tint the shadow: a real one is lit only by skylight and bounce. Reserve `#000` for hard print offset.
- Set an explicit region on any blur above 3% of the mark; the default clips it.

## Surface and contact

Scale blur and offset with the gap; let peak opacity fall as the gap grows: `σ ∝ gap^0.5`, `offset ∝ gap`, `opacity ∝ 1/√gap` `[UNVERIFIED]`, inferred from penumbra optics. Approximate at σ 0.5% of mark per unit of gap, offset 1%, 15% less opacity per height step.

Declare the four deaths of a logo shadow:

1. Apply one uniform `dx`/`dy` across a non-planar mark, fixing one height on geometry that is not a plane.
2. Grow σ past 8–10% of the smaller dimension, where a shadow becomes a glow.
3. Place a shadow on transparent background with nothing to catch it: it vanishes on light, doubles on dark.
4. Ship a contact shadow with no contact, so `dy` reads as levitation.

## Lighting a flat mark

Translate the three-point setup into a 2D document's channels.

| Light | Gradient direction | Stop contrast | Colour temperature | Specular |
|---|---|---|---|---|
| Key | Key azimuth, 225° y-down | ≥25% darker than mid | 3000–4500 K, 25–45° | Exponent 4–16 to 40+ |
| Fill | Opposite, low contrast | ≤12% darker | 6500–9000 K, 200–235° | None |
| Rim | None; an edge effect | n/a | Near-white, brand-tinted | Tight, grazing light |

- Set key to fill at 2:1 general, 8:1 dramatic, 1.5:1 corporate; place the key at 15–70°, normally 45° from subject.
- Run the motivated-light test: name the in-frame or adjacent source, or the light is decoration.

## Rim and edge light

Compute a rim rather than paint one. `feSpecularLighting` on the alpha gradient derives an edge normal perpendicular to the silhouette — a true 2D fresnel term, where a radial gradient is a fake.

```svg
<filter id="rim" x="-35%" y="-35%" width="170%" height="170%"
        color-interpolation-filters="sRGB">
  <feGaussianBlur in="SourceAlpha" stdDeviation="3.5" result="bump"/>
  <feSpecularLighting in="bump" surfaceScale="9" specularExponent="7"
                      lighting-color="#dbeeff" result="spec">
    <feDistantLight azimuth="315" elevation="18"/>
  </feSpecularLighting>
  <feComposite in="spec" in2="SourceAlpha" operator="in" result="edge"/>
  <feMerge>
    <feMergeNode in="SourceGraphic"/><feMergeNode in="edge"/>
  </feMerge>
</filter>
```

- Re-clip to `SourceAlpha`; the lighting primitives emit fully opaque output and unclipped replace the mark with a rectangle.
- Add the specular, never substitute it: `feComposite operator="arithmetic" k3="1"`, rim above the source.
- Default to `feDistantLight`, the one light whose direction does not vary per pixel, so flat input stays flat. A `fePointLight` at `z=0` gives near-black, the normal being perpendicular to it.
- Band `specularExponent` at 4–16 satin, 20–40 gloss, 60+ mirror; hold `specularConstant` at 0.3–1.0.

## Shadow in the alpha master

1. Lose colour at low alpha irrecoverably. Filters work on premultiplied RGBA, so un-premultiplying at 8-bit quantises each channel and at α=0 the original RGB is gone. Never key chroma below α = 8/255.
2. Clip and band additive highlights. A sweep computes `min(1, src + dst)`, and 256 steps per channel contour across any near-white area.
3. Fringe the anti-aliased edges a logo is made of: `yuva420p` subsamples chroma 2×2 and bleeds colour from transparent into opaque pixels `[UNVERIFIED]`.
4. Misread 8-bit alpha as a density channel: a shadow authored at 4K and downscaled to 512 px leaves a 2–3 sample ramp that posterises into a hard ring.

Mitigate in order: render the sweep in 16-bit float and export 10-bit or 16-bit; dither with one-octave `feTurbulence` at about 2/255; hold the peak below 0.92, under the clamp. Author soft shadows at delivery resolution, or twice it.

## Limits

- Do not light a flat brand identity; flatness is the product.
- Do not light a square deliverable that must read at 24 px, where a shadow smears under it.
- Do not light a source flattened to a raster with no plate to receive it.
- Do not light a mark whose geometry already carries depth; the lighting competes with the identity.

## Failure modes

- **Symptom:** the mark reads as a sticker pasted on the page. **Repair:** add contact at σ 0.5–1.5%, dy 0.25–0.75% of mark height, or drop the volume claim.
- **Symptom:** the shadow vanishes on light, doubles on dark. **Repair:** ship flat with a recipe, or bake onto a named surface.
- **Symptom:** edges harden into a rectangle. **Repair:** re-clip the lighting result to `SourceAlpha`.
- **Symptom:** the shadow reads wider in Chrome than in the tool. **Repair:** set `color-interpolation-filters="sRGB"`, halve the blur.
- **Symptom:** exploded parts cast one shadow. **Repair:** filter per part, scaling σ, offset, and opacity by that part's height; one buffer each.

## QA

- Composite on light and on dark; reject a shadow that vanishes on one or doubles on the other.
- Inspect all four canvas edges; confirm no blur, offset, or long-angle shadow crops.
- Compare at 24, 48, and 128 px; confirm the silhouette reads and no shadow exceeds the mark.
- Halve a `drop-shadow()` value back to its tool number; they should match.
- Hold the rim at or above 1.0 px; check the hold frame for filter residue or a region clip.

These are planning ranges and observed behaviours, not a licence to light every mark.
