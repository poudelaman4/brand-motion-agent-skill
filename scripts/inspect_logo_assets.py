from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:
    np = None
    Image = None

try:
    from scipy import ndimage
except ImportError:
    ndimage = None


def inspect(path: Path, minimum_area: int, alpha_threshold: int, max_components: int) -> dict:
    if np is None or Image is None:
        raise RuntimeError("Pillow and NumPy are required.")
    try:
        image = Image.open(path)
        image.load()
    except Exception as exc:
        raise RuntimeError(f"Could not read {path}: {exc}") from exc
    rgba = image.convert("RGBA")
    array = np.asarray(rgba)
    alpha = array[:, :, 3]
    bbox = rgba.getchannel("A").getbbox()
    has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
    result = {
        "path": str(path),
        "format": image.format,
        "mode": image.mode,
        "width": image.width,
        "height": image.height,
        "has_alpha": has_alpha,
        "alpha_bbox": list(bbox) if bbox else None,
        "alpha_pixels": int((alpha > alpha_threshold).sum()),
        "components": [],
        "warnings": [],
    }
    if not has_alpha:
        result["warnings"].append("The source is opaque; alpha separation is unavailable.")
    if bbox is None:
        result["warnings"].append("The image has no visible alpha pixels at the selected threshold.")
        return result
    if ndimage is None:
        result["warnings"].append("SciPy is unavailable; connected-component detection was skipped.")
        return result
    labels, count = ndimage.label(alpha > alpha_threshold)
    objects = ndimage.find_objects(labels)
    components = []
    omitted = 0
    for label, slices in enumerate(objects, 1):
        if slices is None:
            continue
        y0, y1 = slices[0].start, slices[0].stop
        x0, x1 = slices[1].start, slices[1].stop
        area = int((labels[slices] == label).sum())
        if area < minimum_area:
            omitted += 1
            continue
        if len(components) < max_components:
            components.append({"area": area, "bbox": [x0, y0, x1, y1]})
        else:
            omitted += 1
    components.sort(key=lambda item: item["area"], reverse=True)
    result["components"] = components
    result["component_count"] = int(count)
    result["reported_component_count"] = len(components)
    result["omitted_component_count"] = omitted
    result["warnings"].append("Connected components are diagnostic evidence, not guaranteed semantic logo layers.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a logo image's alpha and large connected components.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--minimum-area", type=int, default=20)
    parser.add_argument("--alpha-threshold", type=int, default=0)
    parser.add_argument("--max-components", type=int, default=100)
    args = parser.parse_args()
    if not args.path.exists():
        print(f"Input does not exist: {args.path}", file=sys.stderr)
        return 2
    if args.minimum_area < 1 or not 0 <= args.alpha_threshold <= 255 or args.max_components < 1:
        print("minimum-area and max-components must be positive; alpha-threshold must be 0-255.", file=sys.stderr)
        return 2
    try:
        result = inspect(args.path, args.minimum_area, args.alpha_threshold, args.max_components)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
