# Motion Manifest and Review Contract

A motion manifest makes a logo animation reproducible and reviewable. Use `assets/motion-manifest-template.json` as the executable starting point and validate it with `scripts/validate_motion_spec.py`.

## Required composition fields

```json
{
  "name": "example-logo-reveal",
  "fps": 30,
  "duration_frames": 120,
  "canvas": {"width": 1080, "height": 1080},
  "source_reference": "path/to/approved-static.png",
  "source_checksum": "sha256:...",
  "source_profile": "sRGB",
  "primary_concept": "ORG-01",
  "settle_frame": 96,
  "hold_start_frame": 96,
  "reduced_motion": "Show the approved final state immediately.",
  "background_variants": ["alpha", "white", "brand"],
  "poster_frame": 119,
  "layers": []
}
```

`outputs`, `target_player`, and `renderer` are optional but recommended for production handoff. Use half-open layer intervals `[start_frame, start_frame + duration_frames)`. Require `settle_frame <= hold_start_frame <= poster_frame < duration_frames`.

## Required layer fields

```json
{
  "id": "outer-left",
  "role": "rear-organic",
  "source": "layers/outer-left.png",
  "bounds": [0.0, 0.48, 0.47, 0.62],
  "pivot": [0.47, 0.61],
  "z_index": 1,
  "start_frame": 4,
  "duration_frames": 30,
  "from": {"x": -0.02, "y": 0.003, "scale": 0.9, "rotation": -5, "opacity": 0},
  "to": {"x": 0, "y": 0, "scale": 1, "rotation": 0, "opacity": 1},
  "easing": "organic",
  "confidence": "observed",
  "locked": false,
  "final_state": true
}
```

Bounds use a top-left origin and normalized `[x_min, y_min, x_max, y_max]` coordinates. Pivots use normalized `[x, y]` coordinates and may be outside a tight crop when a semantic anchor is outside visible pixels. `final_state: true` means the layer's `to` transform is the canonical final transform.

## Output entries

An output entry has an `id`, independent `canvas`, `background`, `path`, and optional `codec`. Multiple aspect ratios and backgrounds are separate compositions driven by the same canonical timing model.

## Review statuses

- `PASS`: verified against the reference and target runtime.
- `WARN`: acceptable with a documented limitation, inferred decision, or encoded-output tolerance.
- `BLOCKED`: cannot proceed without source, approval, runtime, or missing information.

## Validation notes

The bundled validator checks required fields, unknown fields, finite numbers, frame ordering, normalized bounds, easing tokens, source paths when requested, and canonical final transforms. It does not prove visual quality; use the QA checklist and decoded frame comparison for that.
