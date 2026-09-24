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

A connected-component scan is diagnostic evidence, not semantic-layer recovery. A reconstruction or redraw is a new source asset and needs approval.
