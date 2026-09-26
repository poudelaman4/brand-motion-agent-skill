# Depth and Material as Craft

Material and depth are claims about a brand's substance, not enhancements; assert one only when the geometry and the delivery target can carry it.

## Contents

- Material is a claim
- The material ladder
- Metal and foil sweeps
- Fresnel and rim falloff
- Depth without 3D
- Occlusion and layering
- The economics
- Limits
- Failure modes
- QA

## Material is a claim

Read `light-and-shadow.md` for shadow and lighting values; apply this file to the surface and to the distance between parts.

Choose a surface to assert something. A flat mark states that the brand is confident in its geometry; a chrome mark states that the brand is buying expense rather than earning it. Require a reason in the brief before either.

**Governing rule:** material cues must agree with each other. A specular highlight on a matte silhouette reads as a bug, not a material.

1. Hold one material per asset; permit two states at most, one accent then the canonical surface.
2. Match the material to the value structure; a mark built on one flat tone cannot carry gloss.
3. Treat a surface claim as provisional until composited on light and on dark.

## The material ladder

| Material | Tells | Fake | Cost | Verdict | Never for |
|---|---|---|---|---|---|
| Flat | One or two values | 2-stop `linear-gradient` | Free | **The correct default** | Nothing |
| Paper / matte | Broad, no specular | 3-stop, darkest ≤15% from mid | Free | Safe; reads as print | A premium claim |
| Satin | One wide highlight | 3–4% light stop; exponent 4–8 | Low | Best premium-without-lying | High-contrast marks |
| Gloss | Narrow highlight, dark band | 1–2% stop; exponent 20–40 | Low | One reveal beat | A resting state |
| Metal | Hard banding, one axis | 6–9 hard stops; `background-clip` | Low CPU, high risk | **Accent only**, 1 frame to 1 s | Restating its own values |
| Foil | Hue cycling, one band | `conic-gradient` + repeats + `color-dodge` | High noise | Accent only, one pass | Uncontrolled backgrounds |
| Glass | Refraction, backdrop | `backdrop-filter: blur()` | Medium | **Almost never for a mark** | Nothing behind it to protect |
| Chrome | A real environment | **Nothing**; needs an HDRI | Renderer | **Never a state**; 400–700 ms | 16–24 px, greyscale |

## Metal and foil sweeps

```css
.metal {
  background-image: linear-gradient(100deg,
    #10131a 0%, #3a4353 12%, #dfe6ef 27%, #7d8b9e 40%,
    #f4f8fc 50%, #6d7a8c 62%, #c8d2de 76%, #2a303b 90%, #10131a 100%);
  background-size: 220% 100%;
  -webkit-background-clip: text; background-clip: text;
  color: transparent;
  animation: sweep 5s linear infinite;
}
@keyframes sweep { from { background-position: 160% 0 } to { background-position: -60% 0 } }
```

```css
.foil {
  background-image:
    repeating-linear-gradient(0deg,  transparent 0 2px, rgb(255 255 255 / .04) 2px 4px),
    repeating-linear-gradient(90deg, transparent 0 2px, rgb(255 255 255 / .04) 2px 4px),
    conic-gradient(from 0deg, #ff0080, #ff8c00, #ffe100, #40ff00, #00cfff, #8000ff, #ff0080);
  background-size: 300% 300%, 100% 100%, 300% 300%;
  -webkit-background-clip: text; background-clip: text;
  color: transparent;
  mix-blend-mode: color-dodge; filter: saturate(1.25);
  animation: foil 6s linear infinite;
}
```

Correct the detail almost everyone gets wrong: **metal is a value pattern with hard stops along a single axis**, not a smooth colour gradient. A smooth 3-stop gradient reads as satin. Space the light stops at 9–15% of the axis and the hue at about 5%, because tight hue spacing makes the band.

Set `background-size` to 200–300% so the sweep enters and exits cleanly. Run both as an accent for a sub-second beat, 400–700 ms once, then return to flat; never hold either as a resting state.

## Fresnel and rim falloff

Set normal-incidence reflectance F₀ at 70–100% for metals and 0–8% for non-metals, default 4%. At grazing angles specular approaches 100%. The term is nothing at normal incidence and everything at grazing, which in 2D is a rim.

| Roughness | Character | `specularExponent` `[UNVERIFIED]` |
|---|---|---:|
| 0.0 | Perfectly sharp reflection | 100+ |
| 0.1–0.2 | Gloss / lacquer | 40–60 |
| 0.3–0.45 | Satin | 12–25 |
| 0.5–0.7 | Eggshell | 5–10 |
| 0.8–1.0 | Matte / chalk | 0–4 |

Build a rim as the two-dimensional form of that falloff. Drive it with a mask or a directional gradient on one axis, never a `radial-gradient`, because a radial gradient produces a circular rim that does not follow the glyph.

## Depth without 3D

Apply the four-channel model and its `z` mappings in `patterns/separation-and-explode.md`; select among the channels here.

| Cue | Communicates | Cost | Portability |
|---|---|---|---|
| Per-part scale | Size constancy | Free | Universal |
| Per-part opacity | Aerial recession | Free | Universal |
| Per-part shadow | Gap, a catcher | Low | Gated in Lottie |
| Per-part blur | Accommodation | Per-frame raster | Browser, video |
| Occlusion order | Which part is front | Free | Universal |
| Size, position | A ground plane | Free | Universal |
| Contrast, saturation | Aerial perspective | Free | Universal |
| Parallax | Camera translation | Free | Universal |
| Selective focus | One sharp subject | Per-layer raster | Browser, video |

Count per-part blur as a per-frame rasterisation cost and hold parts at or near 12. Apply every cue per part; a cue on a whole group is a focus pull, not depth. Paint far parts first.

## Occlusion and layering

Treat 2D paint order as document order: `z-index` has no effect and no CSS corrects it.

Reorder the DOM per frame for the correct fix. Clip a background-coloured copy of the front parts behind the part that must pass behind for the cheap fix. Apply that sandwich wherever parts cross, because it is what makes flat artwork read as layered.

Design the overlap rather than inherit it. Enforce a 15% contrast delta at every crossing, and require the occluded part to lose something behind. A hard-edged overlap with nothing else changing reads as a collage. Flag mutual containment; it cannot be drawn.

## The economics

| Technique | Render cost | Markup | Browser | Lottie | QA |
|---|---|---:|---|---|---|
| Gradient shading | Free | 200–600 B | Safe | Gradient fill | Low |
| Metal sweep | Free on GPU | 200–600 B | Safe | No clip, no blend | Banding |
| Foil plus dodge | Group readback | 400–800 B | Safe | Absent | High |
| Mask-based rim | One buffer | 300–500 B | Safe | Redraw as geometry | Medium |
| `feSpecularLighting` | Sobel per frame | 300–600 B | Safe | No lighting primitive | Re-clip to alpha |
| Per-part blur | Per-layer per frame | 20–60 B/part | Safe | **No blur primitive** | 12-part ceiling |
| `feDisplacementMap` | **Most expensive primitive** | 300–500 B | Safe | Unsupported | Very high |
| `backdrop-filter` | Backdrop readback | 200–400 B | Backdrop root | No backdrop | High |
| Clipped occlusion copy | Two copies per crossing | 100–400 B | Safe | Canvas partial | Medium |

State the constraint plainly: the vector animation format's shape specification has no blur, lighting, displacement, or morphology primitive, so blur-as-depth is not portable there and scale, opacity, and tint must substitute. Hold displacement and turbulence static or omit them, and hold a Lottie deliverable to a flat mark.

## Limits

- Do not add material to a flat brand identity; flatness is the product.
- Do not add depth to a deliverable that must read at 24 px, where a material smears under it.
- Do not add a specular cue to a monochrome asset, where hue carries no information.
- Do not add a shadow to a raster flattened with no plate to receive it.
- Do not add depth where the cue competes with the mark's geometry, and where extrusion invents an unapproved silhouette.

## Failure modes

- **Symptom:** a highlight sits on a matte silhouette. **Repair:** match the surface to the material; specular needs gloss behind it.
- **Symptom:** the mark goes soft as a whole. **Repair:** blur per part; a group blur is a focus pull.
- **Symptom:** metal renders as satin. **Repair:** swap the smooth 3-stop gradient for 6–9 hard alternating stops.
- **Symptom:** a front mark passes behind a back layer. **Repair:** reorder the DOM per frame.
- **Symptom:** the mark turns to mush at 24 px. **Repair:** ship flat as the canonical state.

## QA

- Composite on light and on dark; reject a surface that vanishes on one or doubles on the other.
- Convert to greyscale; reject any material whose tell depends on hue alone.
- Screenshot at the smallest delivery size, 24 px, and confirm the silhouette reads.
- Count blurred parts, hold at or near 12, and measure frame time with the blur live.
- Inspect every crossing at 25%, 50%, 75%, and 100% for an inverting occlusion.
- Verify the export in the named player; confirm the reduced-motion asset is static.

These are planning ranges and `observed` behaviours, not a licence to make every mark material.
