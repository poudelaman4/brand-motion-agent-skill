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
ALLOWED_ROOT = REQUIRED | {"source_checksum", "source_profile", "target_player", "renderer", "outputs"}
TRANSFORM_KEYS = {"x", "y", "scale", "rotation", "opacity"}
LAYER_KEYS = {
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
EASING = {"settle", "enter", "draw", "organic", "snap", "play", "path-linear"}
CONFIDENCE = {"observed", "inferred", "provisional", "blocked"}


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
        if set(layer) != LAYER_KEYS:
            errors.append(f"{prefix} must contain exactly {sorted(LAYER_KEYS)}.")
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
