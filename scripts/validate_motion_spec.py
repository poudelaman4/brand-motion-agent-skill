import argparse
import json
import math
import sys
from pathlib import Path

REQUIRED = {
    "name",
    "fps",
    "duration_frames",
    "canvas",
    "source_reference",
    "primary_concept",
    "settle_frame",
    "hold_start_frame",
    "reduced_motion",
    "background_variants",
    "poster_frame",
    "layers",
}
ALLOWED_ROOT = REQUIRED | {"source_checksum", "source_profile", "target_player", "renderer", "outputs", "detection"}
TRANSFORM_KEYS = {"x", "y", "scale", "rotation", "opacity"}
LAYER_REQUIRED = {
    "id",
    "role",
    "source",
    "bounds",
    "pivot",
    "z_index",
    "start_frame",
    "duration_frames",
    "from",
    "to",
    "easing",
    "confidence",
    "locked",
    "final_state",
}
# Optional per-layer channels for the advanced technique families. A stroke
# reveal, an explode vector, a true path morph, a mask wipe, and a bounded
# effect set are not transforms, so each carries its own channel instead of
# overloading x/y/scale/rotation/opacity.
LAYER_OPTIONAL = {
    "technique",
    "scenario_id",
    "stroke",
    "separation",
    "morph",
    "mask",
    "effects",
}
LAYER_KEYS = LAYER_REQUIRED | LAYER_OPTIONAL
EASING = {"settle", "enter", "draw", "organic", "snap", "play", "path-linear", "morph"}
CONFIDENCE = {"observed", "inferred", "provisional", "blocked"}
DETECTION_CONFIDENCE = {"inferred", "provisional", "blocked"}
TECHNIQUES = {
    "line_draw_on", "multi_stroke_trace", "kinetic_typography", "mask_wipe",
    "mask_wipe_mark", "circular_sweep", "particle_dissolve", "morph_shape",
    "separation_explode", "separation_ordered", "geometric_construction",
    "extrusion_3d", "bounce_elastic", "orbit_rotate", "orbit_rotate_badge",
    "gradient_sweep", "idle_loop", "scroll_scrub", "reduced_motion",
}
COMPLEXITY_BANDS = {"atomic", "geometric", "moderate", "detailed", "illustrative"}
STROKE_KEYS = {"path_length", "dasharray", "dashoffset_from", "dashoffset_to",
               "linecap", "linejoin", "order", "closed", "pen_lift"}
SEPARATION_KEYS = {"axis", "distance", "depth", "order_source"}
MORPH_KEYS = {"path_from", "path_to", "correspondence", "segment_count"}
MASK_KEYS = {"type", "angle", "feather", "from_pct", "to_pct"}
EFFECT_KEYS = {"particle_count", "seed", "lifetime_frames",
               "turbulence_base_frequency", "turbulence_octaves",
               "sweep_type", "sweep_angle", "blend_mode"}
EFFECT_SWEEP_TYPES = {"linear", "radial", "conic", "foil"}
EFFECT_BLEND_MODES = {"normal", "screen", "overlay", "add", "multiply"}
MASK_TYPES = {"alpha", "luma", "vector", "clip", "conic", "band", "wedge"}


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_canvas(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict) or set(value) != {"width", "height"}:
        errors.append(f"{prefix} must contain exactly width and height.")
        return
    for key in ("width", "height"):
        if not is_int(value.get(key)) or value[key] < 1:
            errors.append(f"{prefix}.{key} must be a positive integer.")


def validate_transform(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict) or set(value) != TRANSFORM_KEYS:
        errors.append(f"{prefix} must contain exactly {sorted(TRANSFORM_KEYS)}.")
        return
    for key in TRANSFORM_KEYS:
        if not is_number(value[key]):
            errors.append(f"{prefix}.{key} must be a finite number.")
    if is_number(value.get("scale")) and value["scale"] <= 0:
        errors.append(f"{prefix}.scale must be positive.")
    if is_number(value.get("opacity")) and not 0 <= value["opacity"] <= 1:
        errors.append(f"{prefix}.opacity must be between 0 and 1.")


def validate_stroke(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object.")
        return
    unknown = sorted(set(value) - STROKE_KEYS)
    if unknown:
        errors.append(f"{prefix} contains invalid fields: {unknown}")
    for key in ("path_length", "dasharray", "dashoffset_from", "dashoffset_to"):
        if not is_number(value.get(key)):
            errors.append(f"{prefix}.{key} must be a finite number.")
    if is_number(value.get("path_length")) and value["path_length"] <= 0:
        errors.append(f"{prefix}.path_length must be positive.")
    # A dasharray shorter than the path re-dashes mid-draw and shows a second
    # line, which is the most common draw-on defect.
    if is_number(value.get("dasharray")) and is_number(value.get("path_length")) \
            and value["dasharray"] < value["path_length"]:
        errors.append(f"{prefix}.dasharray must be greater than or equal to path_length.")
    for key in ("linecap", "linejoin"):
        if key in value and value[key] not in {"butt", "round", "square", "miter", "bevel"}:
            errors.append(f"{prefix}.{key} is not a valid value.")
    for key in ("order",):
        if key in value and (not is_int(value[key]) or value[key] < 0):
            errors.append(f"{prefix}.{key} must be a non-negative integer.")
    for key in ("closed", "pen_lift"):
        if key in value and not isinstance(value[key], bool):
            errors.append(f"{prefix}.{key} must be boolean.")


def validate_separation(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object.")
        return
    unknown = sorted(set(value) - SEPARATION_KEYS)
    if unknown:
        errors.append(f"{prefix} contains invalid fields: {unknown}")
    axis = value.get("axis")
    if (not isinstance(axis, list) or len(axis) != 2
            or not all(is_number(item) for item in axis)):
        errors.append(f"{prefix}.axis must contain two finite numbers.")
    if not is_number(value.get("distance")):
        errors.append(f"{prefix}.distance must be a finite number.")
    if "depth" in value and (not is_number(value["depth"]) or not -1 <= value["depth"] <= 1):
        errors.append(f"{prefix}.depth must be between -1 and 1.")
    if "order_source" in value and value["order_source"] not in {"authored", "z_order", "explicit"}:
        errors.append(f"{prefix}.order_source is not a valid value.")


def validate_morph(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object.")
        return
    unknown = sorted(set(value) - MORPH_KEYS)
    if unknown:
        errors.append(f"{prefix} contains invalid fields: {unknown}")
    for key in ("path_from", "path_to"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            errors.append(f"{prefix}.{key} must be a non-empty string.")
    if "correspondence" in value and value["correspondence"] not in {"matched", "resampled"}:
        errors.append(f"{prefix}.correspondence is not a valid value.")
    if "segment_count" in value and (not is_int(value["segment_count"]) or value["segment_count"] < 3):
        errors.append(f"{prefix}.segment_count must be an integer of at least 3.")


def validate_mask(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object.")
        return
    unknown = sorted(set(value) - MASK_KEYS)
    if unknown:
        errors.append(f"{prefix} contains invalid fields: {unknown}")
    if value.get("type") not in MASK_TYPES:
        errors.append(f"{prefix}.type must be one of {sorted(MASK_TYPES)}.")
    for key in ("angle",):
        if key in value and not is_number(value[key]):
            errors.append(f"{prefix}.{key} must be a finite number.")
    if "feather" in value and (not is_number(value["feather"]) or value["feather"] < 0):
        errors.append(f"{prefix}.feather must be a non-negative number.")
    for key in ("from_pct", "to_pct"):
        if key in value and (not is_number(value[key]) or not 0 <= value[key] <= 100):
            errors.append(f"{prefix}.{key} must be between 0 and 100.")


def validate_effects(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object.")
        return
    unknown = sorted(set(value) - EFFECT_KEYS)
    if unknown:
        errors.append(f"{prefix} contains invalid fields: {unknown}")
    if "particle_count" in value and (not is_int(value["particle_count"])
                                      or not 0 <= value["particle_count"] <= 400):
        errors.append(f"{prefix}.particle_count must be an integer between 0 and 400.")
    if "seed" in value and (not isinstance(value["seed"], str) or not value["seed"].strip()):
        errors.append(f"{prefix}.seed must be a non-empty string.")
    if "lifetime_frames" in value and (not is_int(value["lifetime_frames"])
                                       or not 1 <= value["lifetime_frames"] <= 120):
        errors.append(f"{prefix}.lifetime_frames must be an integer between 1 and 120.")
    if "turbulence_base_frequency" in value and (not is_number(value["turbulence_base_frequency"])
                                                 or not 0 < value["turbulence_base_frequency"] <= 1):
        errors.append(f"{prefix}.turbulence_base_frequency must be greater than 0 and at most 1.")
    if "turbulence_octaves" in value and (not is_int(value["turbulence_octaves"])
                                         or not 1 <= value["turbulence_octaves"] <= 8):
        errors.append(f"{prefix}.turbulence_octaves must be an integer between 1 and 8.")
    if "sweep_type" in value and value["sweep_type"] not in EFFECT_SWEEP_TYPES:
        errors.append(f"{prefix}.sweep_type must be one of {sorted(EFFECT_SWEEP_TYPES)}.")
    if "sweep_angle" in value and not is_number(value["sweep_angle"]):
        errors.append(f"{prefix}.sweep_angle must be a finite number.")
    if "blend_mode" in value and value["blend_mode"] not in EFFECT_BLEND_MODES:
        errors.append(f"{prefix}.blend_mode must be one of {sorted(EFFECT_BLEND_MODES)}.")


def validate_recommendation(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object.")
        return
    if set(value) - {"technique", "scenario_id", "score", "reference"}:
        errors.append(f"{prefix} contains invalid fields.")
    if value.get("technique") not in TECHNIQUES:
        errors.append(f"{prefix}.technique must be a known technique key.")
    if not isinstance(value.get("scenario_id"), str) or not value["scenario_id"].strip():
        errors.append(f"{prefix}.scenario_id must be a non-empty string.")
    if "score" in value and not is_number(value["score"]):
        errors.append(f"{prefix}.score must be a finite number.")
    if "reference" in value and (not isinstance(value["reference"], str) or not value["reference"].strip()):
        errors.append(f"{prefix}.reference must be a non-empty string.")


def validate_detection(value: object, errors: list[str]) -> None:
    prefix = "detection"
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object.")
        return
    allowed = {"tool", "capability_rung", "complexity", "complexity_band", "confidence",
               "primary", "supporting", "blocked", "notes"}
    unknown = sorted(set(value) - allowed)
    if unknown:
        errors.append(f"{prefix} contains invalid fields: {unknown}")
    missing = sorted({"confidence", "primary", "supporting"} - set(value))
    if missing:
        errors.append(f"{prefix} is missing required fields: {missing}")
    # A fingerprint-derived recommendation is inferred at best, and provisional
    # on a flattened raster. It is never observed.
    if value.get("confidence") not in DETECTION_CONFIDENCE:
        errors.append(f"{prefix}.confidence must be one of {sorted(DETECTION_CONFIDENCE)}; "
                      "a detection result is never observed.")
    if "capability_rung" in value and (not is_int(value["capability_rung"])
                                       or not 0 <= value["capability_rung"] <= 8):
        errors.append(f"{prefix}.capability_rung must be an integer between 0 and 8.")
    if "complexity" in value and (not is_number(value["complexity"])
                                  or not 0 <= value["complexity"] <= 100):
        errors.append(f"{prefix}.complexity must be a number between 0 and 100.")
    if "complexity_band" in value and value["complexity_band"] not in COMPLEXITY_BANDS:
        errors.append(f"{prefix}.complexity_band must be one of {sorted(COMPLEXITY_BANDS)}.")
    if "primary" in value:
        validate_recommendation(value["primary"], f"{prefix}.primary", errors)
    supporting = value.get("supporting")
    if supporting is not None:
        if not isinstance(supporting, list):
            errors.append(f"{prefix}.supporting must be an array.")
        else:
            # One primary plus at most two supporting gestures.
            if len(supporting) > 2:
                errors.append(f"{prefix}.supporting must hold at most two gestures.")
            for index, item in enumerate(supporting):
                validate_recommendation(item, f"{prefix}.supporting[{index}]", errors)
    blocked = value.get("blocked")
    if blocked is not None:
        if not isinstance(blocked, list):
            errors.append(f"{prefix}.blocked must be an array.")
        else:
            for index, item in enumerate(blocked):
                label = f"{prefix}.blocked[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{label} must be an object.")
                    continue
                if set(item) - {"technique", "scenario_id", "code", "detail", "remedy"}:
                    errors.append(f"{label} contains invalid fields.")
                for key in ("technique", "code", "detail"):
                    if not isinstance(item.get(key), str) or not item[key].strip():
                        errors.append(f"{label}.{key} must be a non-empty string.")
    notes = value.get("notes")
    if notes is not None and (not isinstance(notes, list)
                              or not all(isinstance(item, str) for item in notes)):
        errors.append(f"{prefix}.notes must be an array of strings.")


def validate(data: object, check_files: bool = False, root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["The manifest root must be an object."]
    missing = sorted(REQUIRED - set(data))
    unknown = sorted(set(data) - ALLOWED_ROOT)
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"Unknown root fields: {', '.join(unknown)}")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errors.append("name must be a non-empty string.")
    if not isinstance(data.get("source_reference"), str) or not data["source_reference"].strip():
        errors.append("source_reference must be a non-empty string.")
    if not isinstance(data.get("primary_concept"), str) or not data["primary_concept"].strip():
        errors.append("primary_concept must be a non-empty string.")
    if not is_number(data.get("fps")) or data["fps"] <= 0:
        errors.append("fps must be a positive finite number.")
    duration = data.get("duration_frames")
    if not is_int(duration) or duration < 1:
        errors.append("duration_frames must be a positive integer.")
    validate_canvas(data.get("canvas"), "canvas", errors)
    for key in ("settle_frame", "hold_start_frame", "poster_frame"):
        value = data.get(key)
        if not is_int(value) or value < 0:
            errors.append(f"{key} must be a non-negative integer.")
    if is_int(duration):
        for key in ("settle_frame", "hold_start_frame", "poster_frame"):
            value = data.get(key)
            if is_int(value) and value >= duration:
                errors.append(f"{key} must be less than duration_frames.")
    if is_int(data.get("settle_frame")) and is_int(data.get("hold_start_frame")) and data["settle_frame"] > data["hold_start_frame"]:
        errors.append("settle_frame must be less than or equal to hold_start_frame.")
    if is_int(data.get("hold_start_frame")) and is_int(data.get("poster_frame")) and data["hold_start_frame"] > data["poster_frame"]:
        errors.append("hold_start_frame must be less than or equal to poster_frame.")
    if not isinstance(data.get("reduced_motion"), str) or not data["reduced_motion"].strip():
        errors.append("reduced_motion must be a non-empty string.")
    variants = data.get("background_variants")
    if not isinstance(variants, list) or not variants or not all(isinstance(value, str) and value.strip() for value in variants):
        errors.append("background_variants must be a non-empty array of non-empty strings.")
    outputs = data.get("outputs")
    if outputs is not None:
        if not isinstance(outputs, list):
            errors.append("outputs must be an array when present.")
        else:
            output_ids: set[str] = set()
            for index, output in enumerate(outputs):
                prefix = f"outputs[{index}]"
                if not isinstance(output, dict) or set(output) - {"id", "canvas", "background", "path", "codec"}:
                    errors.append(f"{prefix} contains invalid fields.")
                    continue
                output_id = output.get("id")
                if not isinstance(output_id, str) or not output_id.strip():
                    errors.append(f"{prefix}.id must be a non-empty string.")
                elif output_id in output_ids:
                    errors.append(f"Duplicate output id: {output_id}")
                else:
                    output_ids.add(output_id)
                validate_canvas(output.get("canvas"), f"{prefix}.canvas", errors)
                for key in ("background", "path"):
                    if not isinstance(output.get(key), str) or not output[key].strip():
                        errors.append(f"{prefix}.{key} must be a non-empty string.")
    if "detection" in data:
        validate_detection(data["detection"], errors)
    layers = data.get("layers")
    if not isinstance(layers, list) or not layers:
        errors.append("layers must be a non-empty array.")
        return errors
    ids: set[str] = set()
    for index, layer in enumerate(layers):
        prefix = f"layers[{index}]"
        if not isinstance(layer, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        if set(layer) - LAYER_KEYS:
            errors.append(f"{prefix} contains invalid fields: {sorted(set(layer) - LAYER_KEYS)}.")
        if LAYER_REQUIRED - set(layer):
            errors.append(f"{prefix} is missing required fields: "
                          f"{sorted(LAYER_REQUIRED - set(layer))}.")
        for key in ("id", "role", "source", "easing"):
            if not isinstance(layer.get(key), str) or not layer[key].strip():
                errors.append(f"{prefix}.{key} must be a non-empty string.")
        layer_id = layer.get("id")
        if isinstance(layer_id, str) and layer_id in ids:
            errors.append(f"Duplicate layer id: {layer_id}")
        if isinstance(layer_id, str):
            ids.add(layer_id)
        bounds = layer.get("bounds")
        if not isinstance(bounds, list) or len(bounds) != 4 or not all(is_number(value) and 0 <= value <= 1 for value in bounds):
            errors.append(f"{prefix}.bounds must contain four normalized finite numbers.")
        elif bounds[2] <= bounds[0] or bounds[3] <= bounds[1]:
            errors.append(f"{prefix}.bounds must have positive width and height.")
        pivot = layer.get("pivot")
        if not isinstance(pivot, list) or len(pivot) != 2 or not all(is_number(value) and 0 <= value <= 1 for value in pivot):
            errors.append(f"{prefix}.pivot must contain two normalized finite numbers.")
        if not is_int(layer.get("z_index")):
            errors.append(f"{prefix}.z_index must be an integer.")
        start = layer.get("start_frame")
        length = layer.get("duration_frames")
        if not is_int(start) or start < 0:
            errors.append(f"{prefix}.start_frame must be a non-negative integer.")
        if not is_int(length) or length < 1:
            errors.append(f"{prefix}.duration_frames must be a positive integer.")
        if is_int(duration) and is_int(start) and is_int(length) and start + length > duration:
            errors.append(f"{prefix} ends after duration_frames.")
        if layer.get("final_state") is True and is_int(data.get("hold_start_frame")) and is_int(start) and is_int(length) and start + length > data["hold_start_frame"]:
            errors.append(f"{prefix} is marked final_state but ends after hold_start_frame.")
        validate_transform(layer.get("from"), f"{prefix}.from", errors)
        validate_transform(layer.get("to"), f"{prefix}.to", errors)
        if layer.get("easing") not in EASING:
            errors.append(f"{prefix}.easing must be one of {sorted(EASING)}.")
        if layer.get("confidence") not in CONFIDENCE:
            errors.append(f"{prefix}.confidence must be one of {sorted(CONFIDENCE)}.")
        if not isinstance(layer.get("locked"), bool):
            errors.append(f"{prefix}.locked must be boolean.")
        if not isinstance(layer.get("final_state"), bool):
            errors.append(f"{prefix}.final_state must be boolean.")
        if "technique" in layer and layer["technique"] not in TECHNIQUES:
            errors.append(f"{prefix}.technique must be a known technique key.")
        if "scenario_id" in layer and (not isinstance(layer["scenario_id"], str)
                                       or not layer["scenario_id"].strip()):
            errors.append(f"{prefix}.scenario_id must be a non-empty string.")
        if "stroke" in layer:
            validate_stroke(layer["stroke"], f"{prefix}.stroke", errors)
        if "separation" in layer:
            validate_separation(layer["separation"], f"{prefix}.separation", errors)
        if "morph" in layer:
            validate_morph(layer["morph"], f"{prefix}.morph", errors)
        if "mask" in layer:
            validate_mask(layer["mask"], f"{prefix}.mask", errors)
        if "effects" in layer:
            validate_effects(layer["effects"], f"{prefix}.effects", errors)
        # A stroke reveal and a true morph both resolve to the canonical final
        # transform, so neither may borrow the transform channel to animate.
        if "stroke" in layer and layer.get("easing") not in {"draw", "path-linear", "enter", "settle"}:
            errors.append(f"{prefix}.easing must be draw or path-linear for a stroke layer.")
        if "morph" in layer and layer.get("easing") != "morph":
            errors.append(f"{prefix}.easing must be morph for a morph layer.")
        to = layer.get("to")
        if layer.get("final_state") is True and isinstance(to, dict) and set(to) == TRANSFORM_KEYS and all(is_number(to.get(key)) for key in TRANSFORM_KEYS):
            canonical = {"x": 0, "y": 0, "scale": 1, "rotation": 0, "opacity": 1}
            if any(abs(to[key] - canonical[key]) > 1e-9 for key in canonical):
                errors.append(f"{prefix}.to must be canonical when final_state is true.")
        if check_files and root is not None and isinstance(layer.get("source"), str) and not layer["source"].startswith(("http://", "https://")):
            source_path = Path(layer["source"])
            if not source_path.is_absolute():
                source_path = root / source_path
            if not source_path.exists():
                errors.append(f"{prefix}.source does not exist: {source_path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an animation-logo motion manifest.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--check-files", action="store_true", help="Check that referenced layer files exist relative to the manifest.")
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Could not parse {args.path}: {exc}", file=sys.stderr)
        return 2
    errors = validate(data, args.check_files, args.path.parent)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: motion manifest is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
