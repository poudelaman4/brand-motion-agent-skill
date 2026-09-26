# Bundled Utilities

Six scripts ship with the skill. Run them from the skill root or with absolute paths. Python 3.10+ is required; optional packages are listed in `requirements.txt`, and every script degrades rather than failing when one is missing.

## Contents

- Choosing a utility
- Structure and recommendation
- Manifest validation
- Source inspection
- Checkpoint evidence
- Final-state comparison
- Package self-check
- Limits

## Choosing a utility

| Need | Script | Runtime |
|---|---|---|
| What can this asset support, and what fits the brand | `profile_logo.py` | stdlib for SVG; Pillow and NumPy for raster, SciPy for component metrics |
| Is this manifest deliverable | `validate_motion_spec.py` | stdlib |
| What is actually in this flattened raster | `inspect_logo_assets.py` | Pillow and NumPy; SciPy for components |
| Show the transition honestly | `make_checkpoint_contact_sheet.py` | FFmpeg |
| Prove the last frame matches the source | `compare_final_frame.py` | FFmpeg, Pillow, NumPy |
| Did an edit break the package | `check_skill.py` | stdlib |

Run `profile_logo.py` and `validate_motion_spec.py` in every mode. The rest belong to `produce`.

## Structure and recommendation

```bash
python scripts/profile_logo.py path/to/logo.svg --register <register> [--frequency <band>]
python scripts/profile_logo.py path/to/logo.png --register corporate --frequency daily
python scripts/profile_logo.py path/to/logo.svg --register heritage --draw-plan
python scripts/profile_logo.py path/to/logo.svg --register premium --json
```

Reports the structural fingerprint, the capability rung, ranked techniques, gated techniques with their gate codes, the taste budget, and the register's vetoes. `--register` is required and the script exits 2 without it, because taste is a judgement about the brand and not a property of the file.

| Flag | Effect |
|---|---|
| `--register` | One of the eleven registers. Required for any profiling run. |
| `--frequency` | `rare`, `occasional`, `daily`, `frequent`, `keyboard`. Scales the duration, gesture, and overshoot ceilings. |
| `--draw-plan` | Adds the stroke draw-on ordering: endpoint graph, Eulerian check, pen-lift count, per-path duration. |
| `--min-confidence` | Suppress techniques scoring below a floor. |
| `--json` | Machine-readable only. |
| `--self-test` | Dependency-free smoke test. Needs no Pillow, NumPy, or SciPy. |

A recommendation is `inferred` on a vector source and `provisional` on a flattened raster, and never `observed`. The script does not read PDF, EPS, or AI sources.

## Manifest validation

```bash
python scripts/validate_motion_spec.py path/to/motion-spec.json
python scripts/validate_motion_spec.py path/to/motion-spec.json --check-files
```

Exit 0 passes, 1 fails with a list of errors, 2 cannot parse the file. `--check-files` additionally resolves every layer's `source` path relative to the manifest.

The validator enforces more than shape. It rejects a dash array shorter than its path, a stroke or morph layer that does not keep the canonical final transform, a `detection` block with no register and no taste budget, a primary the register vetoes, a taste budget that does not match its register and frequency, and a shadow with no declared catcher.

## Source inspection

```bash
python scripts/inspect_logo_assets.py path/to/logo.png
python scripts/inspect_logo_assets.py path/to/logo.png --minimum-area 40 --alpha-threshold 8
```

Reports format, dimensions, alpha bounds, alpha pixel count, and large connected components. `--minimum-area` sets the component area floor, `--alpha-threshold` sets the alpha cutoff from 0 to 255, and `--max-components` caps how many are reported.

Reads raster only; an SVG fails with a clear error. Connected components are diagnostic evidence, not guaranteed semantic layers. This script is superseded by `profile_logo.py` for deciding technique and kept for quick raster triage.

## Checkpoint evidence

```bash
python scripts/make_checkpoint_contact_sheet.py --input video.mp4 --output sheet.jpg --frames 0,30,60,96,119
python scripts/make_checkpoint_contact_sheet.py --input video.mp4 --output sheet.jpg --manifest motion-spec.json
python scripts/make_checkpoint_contact_sheet.py --input video.mp4 --output sheet.png --background checkerboard
```

Extracts exact frames into one labelled sheet. `--frames` takes an explicit list, `--times` takes seconds, and `--manifest` picks the checkpoints from a manifest automatically. `--background` accepts `white`, `black`, or `checkerboard`; use `checkerboard` when the asset has alpha.

Requires FFmpeg on the path. Frame numbers are zero-based, so the last frame of a 120-frame render is 119.

## Final-state comparison

```bash
python scripts/compare_final_frame.py --reference reference.png --encoded video.mp4 --frame 119 --tolerance 0.03
```

Compares one decoded frame against a reference and reports mean absolute error and PSNR per channel, alpha-aware. `--tolerance` sets the pass bar, `--resize` matches dimensions before comparing, `--require-alpha` fails when the encoded file has no alpha, and `--allow-opaque` compares an opaque white or brand render against a transparent reference on purpose.

This checks the encoded output, which is not the same as checking canonical geometry. A codec-tolerant RGB comparison passing does not prove the geometry is exact; the canonical check is the manifest's final-state rule.

## Package self-check

```bash
python scripts/check_skill.py
```

Dependency-free. Validates frontmatter and description length, that every backticked path in `SKILL.md` and across `references/` resolves, that the `SKILL.md` body is inside the specification's line and token guidance, that the schema parses, that eval fixtures exist, that the manifest validator passes the valid fixtures and rejects the invalid one, that the shipped manifest template satisfies the contract, that the profiler self-test passes, that the taste gate applies, and that volatile platform figures carry a `verified_on` date inside the 90-day horizon.

Run it after any edit to this package. A failure names the file and the path.

## Limits

- Do not treat a utility's output as an approval. The profiler ranks; the register vetoes; the user decides.
- Do not skip the profiler because the asset looks obvious. The gates catch live text, traced contours, and single-component rasters that are invisible in a thumbnail.
- Do not use `inspect_logo_assets.py` to justify independent layer motion. Component counts are not layers.
- Do not run the contact sheet and the final-frame check against different renders. The evidence is only valid when both come from the delivered file.
- Do not edit a utility to make a check pass. The checks are the contract.
