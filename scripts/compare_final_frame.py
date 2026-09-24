from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:
    np = None
    Image = None


def parse_rate(value: str) -> float:
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        return float(numerator) / float(denominator)
    return float(value)


def probe_video(video: Path) -> tuple[int, str]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_frames,avg_frame_rate,duration,pix_fmt:format=duration",
        "-of",
        "json",
        str(video),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    raw_count = stream.get("nb_frames")
    if raw_count not in {None, "", "N/A"}:
        count = int(raw_count)
    else:
        rate = stream.get("avg_frame_rate") or "0/0"
        fps = parse_rate(rate) if rate not in {"0/0", "N/A", ""} else 0.0
        duration = float(stream.get("duration") or data.get("format", {}).get("duration") or 0)
        if fps <= 0 or duration <= 0:
            raise ValueError("The encoded stream did not report an exact frame count or usable frame rate.")
        count = max(1, int(round(duration * fps)))
    return count, str(stream.get("pix_fmt", ""))


def extract_frame(video: Path, frame: int, target: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(video),
            "-vf",
            f"select=eq(n\\,{frame})",
            "-vsync",
            "0",
            "-frames:v",
            "1",
            str(target),
        ],
        check=True,
    )
    if not target.exists() or target.stat().st_size == 0:
        raise RuntimeError(f"FFmpeg did not produce frame {frame}.")


def composite(image: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    base = Image.new("RGBA", rgba.size, (*background, 255))
    base.alpha_composite(rgba)
    return base.convert("RGB")


def metrics(reference: Image.Image, actual: Image.Image, compare_alpha: bool) -> dict[str, float | None | bool]:
    ref_rgba = np.asarray(reference.convert("RGBA"), dtype=np.float32) / 255.0
    act_rgba = np.asarray(actual.convert("RGBA"), dtype=np.float32) / 255.0
    ref_rgb = np.asarray(composite(reference, (255, 255, 255)), dtype=np.float32) / 255.0
    act_rgb = np.asarray(composite(actual, (255, 255, 255)), dtype=np.float32) / 255.0
    rgb_error = float(np.mean(np.abs(ref_rgb - act_rgb)))
    alpha_error = float(np.mean(np.abs(ref_rgba[:, :, 3] - act_rgba[:, :, 3]))) if compare_alpha else None
    mse = float(np.mean((ref_rgb - act_rgb) ** 2))
    psnr = None if mse == 0 else float(10.0 * math.log10(1.0 / mse))
    return {"rgb_mae": rgb_error, "alpha_mae": alpha_error, "rgb_psnr_db": psnr, "alpha_comparable": compare_alpha}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare a decoded video frame with an approved reference image.")
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--encoded", type=Path, required=True)
    parser.add_argument("--frame", type=int, default=-1)
    parser.add_argument("--tolerance", type=float, default=0.03)
    parser.add_argument("--resize", action="store_true")
    parser.add_argument("--require-alpha", action="store_true")
    parser.add_argument("--allow-opaque", action="store_true", help="Allow an opaque encoded output to be compared to a transparent reference over white.")
    args = parser.parse_args()
    if np is None or Image is None:
        print("NumPy and Pillow are required.", file=sys.stderr)
        return 2
    if not args.reference.exists() or not args.encoded.exists():
        print("Reference and encoded files must exist.", file=sys.stderr)
        return 2
    if not math.isfinite(args.tolerance) or args.tolerance < 0:
        print("--tolerance must be a finite non-negative number.", file=sys.stderr)
        return 2
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("FFmpeg and FFprobe are required.", file=sys.stderr)
        return 2
    try:
        with Image.open(args.reference) as source:
            reference = source.convert("RGBA").copy()
        with tempfile.TemporaryDirectory(prefix="logo-compare-") as temporary:
            target = Path(temporary) / "frame.png"
            count, pixel_format = probe_video(args.encoded)
            frame = count - 1 if args.frame < 0 else args.frame
            if frame < 0 or frame >= count:
                raise ValueError(f"Requested frame {frame} is outside 0-{count - 1}.")
            extract_frame(args.encoded, frame, target)
            with Image.open(target) as source:
                actual = source.convert("RGBA").copy()
        if reference.size != actual.size:
            if not args.resize:
                raise ValueError(f"Reference size {reference.size} differs from encoded frame size {actual.size}; use --resize only when intentional.")
            actual = actual.resize(reference.size, Image.Resampling.LANCZOS)
        reference_has_alpha = bool(np.asarray(reference.convert("RGBA"))[:, :, 3].min() < 255)
        encoded_has_alpha = any(token in pixel_format.lower() for token in ("rgba", "argb", "bgra", "abgr", "yuva"))
        if args.require_alpha and not encoded_has_alpha:
            raise ValueError(f"The encoded stream pixel format {pixel_format!r} has no detectable alpha channel.")
        if reference_has_alpha and not encoded_has_alpha and not args.allow_opaque:
            raise ValueError("The reference has transparency but the encoded stream is opaque; pass --allow-opaque only when that background change is intentional.")
        compare_alpha = reference_has_alpha and encoded_has_alpha
        result = {"frame": frame, "pixel_format": pixel_format, "reference_size": list(reference.size), "encoded_size": list(actual.size), **metrics(reference, actual, compare_alpha)}
        result["pass"] = result["rgb_mae"] <= args.tolerance and (not compare_alpha or result["alpha_mae"] <= args.tolerance)
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Comparison failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
