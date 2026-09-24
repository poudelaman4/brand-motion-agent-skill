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

## Repair checklist

1. Reclassify the source capability.
2. Mark unknown decisions as provisional or blocked.
3. Rebuild the motion manifest from the canonical reference.
4. Render exact checkpoint and poster frames.
5. Re-run visual, encoded-output, target-player, and reduced-motion checks.
