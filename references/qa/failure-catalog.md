# Failure Catalog

## Contents

- Layer and source failures
- Motion failures
- Typography failures
- Delivery failures
- Repair checklist

## Layer and source failures

### Connected components treated as semantic layers

**Symptom:** antialias fragments, shadows, or touching shapes become separate “petals.”
**Repair:** inspect each candidate alone and in context; request the original layered/vector source or use an approved group.

### Hidden pixels invented

**Symptom:** a leaf or letter reveals detail that was not visible in the source.
**Repair:** mark independent motion blocked, request a reconstruction, or use a whole-mark/group fallback.

### Baked matte or halo

**Symptom:** white/black fringe appears after moving a layer.
**Repair:** inspect alpha, clean edges, and composite over multiple backgrounds.

### Noisy raster crossfade ghost

**Symptom:** a pale duplicate contour, broken ring, or matte fragment appears only while an extracted layer is partially transparent.
**Cause:** low-alpha ringing, residual pixels, crop contamination, or an already-upscaled raster layer is being crossfaded with cleaner vector or whole-mark geometry.
**Repair:** prefer approved vector geometry; otherwise rebuild from original-resolution pixels, prune residual components, inspect multiple backgrounds, render direct start/mid/end stills, decode the encoded transition frames, and fall back to the clean vector or whole-mark reveal instead of hiding the ghost with effects.

### Parts separated in a flattened raster

**Symptom:** a wordmark never resolves; letters arrive as unrecognizable fragments, and no checkpoint frame reads as the name.
**Repair:** fall back to a directional mask wipe for the whole word, or work from an approved manual part list. Never segment a flattened wordmark per frame; record the parts as `blocked` until they are approved, per `patterns/wordmark-and-lockup.md` and `patterns/separation-and-explode.md`.

### Symmetry-driven recommendation from an ambiguous detection

**Symptom:** a symmetry-dependent recommendation fires on a mark with no real symmetry, such as a uniform blob that scores symmetric on every axis.
**Cause:** the raw mirror score measures the best axis against 1.0 rather than against the mean score across all sampled axes, so a shape that matches itself equally in every direction reads as strongly symmetric.
**Repair:** subtract the mean axis baseline before accepting a symmetry value, cross-check the reflected half against the raster ink mask, and label the result `inferred` or `provisional` until it is confirmed visually. Halve every symmetry-driven rule while the detection stays ambiguous, per `technique-selection.md`.

## Motion failures

### Detached pivot

**Symptom:** a leaf floats or rotates around the center of its crop.
**Repair:** use a root/base pivot and show a pivot overlay.

### Queued sequence

**Symptom:** every element waits for the previous one, making the logo feel slow or mechanical.
**Repair:** overlap two meaningful phases and start the wordmark when the mark is readable.

### Late correction

**Symptom:** elements still move during the final hold.
**Repair:** move the settle frame earlier, shorten stagger, or increase duration.

### Generic effects

**Symptom:** glow, particles, glitch, or bounce obscure the silhouette without expressing the brand.
**Repair:** remove the effect or reduce it to a subordinate accent.

### Dash array shorter than the path

**Symptom:** a second line appears behind the drawing stroke, and the contour reads as doubled once the reveal completes.
**Cause:** a `stroke-dasharray` below the measured path length re-dashes the remainder as a fresh dash, so the tail of the path is drawn a second time.
**Repair:** measure each subpath, set `dasharray` to the measured length, and confirm at 100% reveal that exactly one line covers each subpath. Never estimate a length from the bounding box; read `motion-foundations.md` for the dash arithmetic.

### Draw starts on the axis of symmetry

**Symptom:** a seam or a blunt lump sits on the mirror line of a closed symmetric mark, and the contour looks broken at 200% zoom.
**Cause:** the reveal begins and ends at the same point on the closed subpath, so the two caps coincide instead of joining.
**Repair:** move the start to the apex and draw the mirrored halves in sequence, or split the mark into two subpaths. Prefer a free degree-one endpoint ahead of any mirror line.

## Typography failures

### Font substitution

**Symptom:** glyphs, kerning, or language support change in the renderer.
**Repair:** outline or embed the approved font and compare the static master.

### Arbitrary letter bounce

**Symptom:** every glyph uses the same large spring or rotation.
**Repair:** use a small reading-order stagger, mask, or one wordmark-level settle.

### Wrong reading order

**Symptom:** RTL, vertical, or non-Latin text animates in the wrong sequence.
**Repair:** declare text direction and use language-appropriate order.

## Delivery failures

### Preview passes but encoded output fails

**Symptom:** codec, alpha, color range, or chunk boundaries change the result.
**Repair:** probe and decode the actual file; test the target player and fallback.

### Performance collapse

**Symptom:** full-canvas transparent layers exhaust memory or produce decode warnings.
**Repair:** use tight crops, explicit bounds, fewer simultaneous alpha surfaces, and conservative concurrency.

### Non-deterministic render

**Symptom:** two renders of the same frame range differ; particles, grain, or noise change between passes and the poster frame will not reproduce.
**Cause:** runtime randomness, wall-clock time, or a module-scope counter supplies positions, lifetimes, and turbulence phases instead of a value derived from the frame number.
**Repair:** derive every stochastic value from the frame number and a stable seed string, bake the sample table, and render the same range twice to confirm identical output. Treat runtime randomness as `blocked` in a frame-driven renderer, per `patterns/matter-and-particles.md`.

## Repair checklist

1. Reclassify the source capability.
2. Mark unknown decisions as provisional or blocked.
3. Rebuild the motion manifest from the canonical reference.
4. Render exact checkpoint and poster frames.
5. Re-run visual, encoded-output, target-player, and reduced-motion checks.
