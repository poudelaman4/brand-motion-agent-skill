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
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None


def parse_rate(value: str) -> float:
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        return float(numerator) / float(denominator)
    return float(value)


def probe_video(path: Path) -> tuple[int, float]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_frames,avg_frame_rate,duration:format=duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/0"
    fps = parse_rate(rate) if rate not in {"0/0", "N/A"} else 0.0
    raw_count = stream.get("nb_frames")
    if raw_count not in {None, "", "N/A"}:
        count = int(raw_count)
    else:
        duration = float(stream.get("duration") or data.get("format", {}).get("duration") or 0)
        count = max(1, int(round(duration * fps))) if fps > 0 else 1
    if count < 1:
        raise ValueError("The video stream did not report a usable frame count.")
    return count, fps


def parse_numbers(value: str, label: str) -> list[float]:
    try:
        numbers = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise ValueError(f"{label} must be comma-separated numbers.") from exc
    if not numbers or any(not math.isfinite(number) for number in numbers):
        raise ValueError(f"{label} must contain finite numbers.")
    return numbers


def parse_frames(value: str) -> list[int]:
    numbers = parse_numbers(value, "--frames")
    frames = []
    for number in numbers:
        if number < 0 or not number.is_integer():
            raise ValueError("--frames must contain non-negative integers.")
        frames.append(int(number))
    return frames


def checkerboard(size: tuple[int, int], cell: int = 24) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, (245, 245, 245, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, height, cell):
        for x in range(0, width, cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(width, x + cell), min(height, y + cell)), fill=(220, 220, 220, 255))
    return image


def composite(image: Image.Image, background: str) -> Image.Image:
    rgba = image.convert("RGBA")
    if background == "black":
        base = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    elif background == "checkerboard":
        base = checkerboard(rgba.size)
    else:
        base = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    base.alpha_composite(rgba)
    return base.convert("RGB")


def manifest_frames(path: Path) -> tuple[list[int], int | None, int | None]:
    data = json.loads(path.read_text(encoding="utf-8"))
    duration = int(data["duration_frames"])
    settle = int(data.get("settle_frame", max(0, round(duration * 0.8))))
    poster = int(data.get("poster_frame", duration - 1))
    count = duration
    values = [0, round((count - 1) * 0.25), round((count - 1) * 0.5), round((count - 1) * 0.75), max(0, settle - 1), settle, poster]
    return sorted(set(min(max(value, 0), count - 1) for value in values)), settle, poster


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a frame-accurate checkpoint contact sheet from a logo video.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frames", help="Comma-separated exact video frame indices.")
    parser.add_argument("--times", help="Comma-separated relative times from 0 to 1 when --frames is omitted.")
    parser.add_argument("--manifest", type=Path, help="Motion manifest used to select settle and poster frames.")
    parser.add_argument("--background", choices=("white", "black", "checkerboard"), default="white")
    parser.add_argument("--columns", type=int, default=3)
    args = parser.parse_args()
    if Image is None or ImageDraw is None:
        print("Pillow is required. Install Pillow before using this utility.", file=sys.stderr)
        return 2
    if not args.input.exists():
        print(f"Input does not exist: {args.input}", file=sys.stderr)
        return 2
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("FFmpeg and FFprobe are required.", file=sys.stderr)
        return 2
    if args.columns < 1:
        print("--columns must be at least 1.", file=sys.stderr)
        return 2
    try:
        count, fps = probe_video(args.input)
        if args.frames:
            frames = parse_frames(args.frames)
        elif args.manifest:
            frames, _, _ = manifest_frames(args.manifest)
        else:
            relative = parse_numbers(args.times or "0,0.25,0.5,0.75,1", "--times")
            if any(value < 0 or value > 1 for value in relative):
                raise ValueError("--times values must be between 0 and 1.")
            frames = sorted(set(min(count - 1, max(0, round(value * (count - 1)))) for value in relative))
        if any(frame < 0 or frame >= count for frame in frames):
            raise ValueError(f"Requested frames must be between 0 and {count - 1}.")
        with tempfile.TemporaryDirectory(prefix="logo-contact-") as temporary:
            temporary_dir = Path(temporary)
            images = []
            for index, frame in enumerate(frames):
                target = temporary_dir / f"frame-{index:02d}.png"
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-v",
                        "error",
                        "-i",
                        str(args.input),
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
                with Image.open(target) as image:
                    images.append((frame, composite(image, args.background)))
            sample = images[0][1]
            cell_width = min(480, sample.width)
            cell_height = int(sample.height * cell_width / sample.width)
            label_height = 30
            columns = args.columns
            rows = (len(images) + columns - 1) // columns
            sheet = Image.new("RGB", (cell_width * columns, (cell_height + label_height) * rows), "white")
            draw = ImageDraw.Draw(sheet)
            for index, (frame, image) in enumerate(images):
                x = (index % columns) * cell_width
                y = (index // columns) * (cell_height + label_height)
                sheet.paste(image.resize((cell_width, cell_height)), (x, y))
                seconds = frame / fps if fps > 0 else 0
                draw.text((x + 8, y + cell_height + 7), f"frame {frame} | {seconds:.3f}s", fill="black")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            sheet.save(args.output, quality=92)
    except (subprocess.CalledProcessError, OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"Contact sheet failed: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output} using {count} video frames at {fps:.3f} fps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
