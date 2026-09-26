# Pattern Feasibility

Use this table before choosing a motion pattern. It describes the safest source type and the fallback when the source is flattened.

| Pattern family | Vector/layered source | Flattened fallback |
|---|---|---|
| Organic bloom | Root-based leaf/petal transforms and masks | Whole-mark mask, silhouette reveal, or manually approved groups |
| Geometric assembly | Module transforms, connectors, masks | Whole-mark fade/crop; independent modules blocked |
| Monogram weave | Approved over/under mattes and paths | Whole-mark reveal; do not infer weave order |
| Wordmark write-on | Real stroke/path data or approved mask | Whole-word mask/fade; no fake writing order |
| Badge construction | Named rings, type, separators, and text-on-path | Whole-badge mask or approved grouped regions |
| Interactive state | Named state layers and runtime triggers | Static states only until layers are approved |
| Line drawing and stroke trace | Authored stroke paint, open subpaths, monoline weight | Blocked: a traced or filled outline has no stroke to reveal |
| Separation and explode | Two or more independently addressable parts with known bounds | Band, wedge, or conic mask separation on identical copies; never per-letter slicing |
| Kinetic typography | Outlined glyph paths with recorded advances, or live text with a guaranteed font | Whole-word directional mask; no per-glyph timing |
| Geometric construction | Primitive parts, published grid, rotational symmetry | Blocked: reconstruction invents geometry the source does not contain |
| Gradient and light sweep | A gradient or multi-colour surface to sweep | Blocked on monochrome art; nothing to sweep |
| Matter and particles | A sampleable silhouette, alpha, or a filter-capable runtime | Alpha-threshold dissolve and turbulence only; never a semantic particle field |
| Idle and ambient loop | A loopable asset and a stated resource budget | Static rest state plus reduced-motion hold |
| Morph | Two approved states with matched segment counts and correspondence | Blocked: re-winding subpaths breaks parity-managed counters |

A connected-component scan is diagnostic evidence, not semantic-layer recovery. A reconstruction or redraw is a new source asset and needs approval.

Run `scripts/profile_logo.py` before choosing. It reports which of these rows apply, the gate code for each technique it rules out, and the confidence behind the recommendation. Read `technique-selection.md` for the gate table.
