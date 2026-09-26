#!/usr/bin/env python3
"""Profile a logo and rank the motion techniques its structure actually supports.

The profiler answers two questions in order:

1. What is in this file? A structural fingerprint measured from the asset -
   vector path census, open/closed subpath lengths, stroke paint, counters,
   components, symmetry, complexity - each value labelled `observed`,
   `inferred`, or `provisional`.
2. What follows from it? A ranked shortlist of at most one primary technique
   plus two supporting gestures, every gated technique reported with a
   `blocked_by` reason, and the rules that fired with their weights.

Vector sources are analysed with the standard library only, so profiling an SVG
works with no third-party packages installed. Raster sources need Pillow and
NumPy, and SciPy for the component and stroke-width metrics; when a dependency
is missing the affected metrics are reported as `null` with a warning rather
than guessed, and the global confidence is reduced.

The profiler never claims semantic layers. On a flattened raster every
component-derived value is `provisional`: connected components are evidence,
not layers. Recommendations are therefore `inferred` on vector sources and
`provisional` on raster sources, never `observed`.

Read references/technique-selection.md for the rule table, the capability
ladder, and the conflict-resolution rules this script implements.

Usage:
    python scripts/profile_logo.py path/to/logo.svg
    python scripts/profile_logo.py path/to/logo.png --min-confidence 0.3
    python scripts/profile_logo.py --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "{http://www.w3.org/2000/svg}"

# --------------------------------------------------------------------------
# Tunable constants. Every threshold the rule table depends on lives here.
# --------------------------------------------------------------------------

EPS = 1e-9
FLATTEN_SEGMENTS = 16          # polyline segments per curve
JUNCTION_TOLERANCE = 0.012     # endpoint clustering, fraction of bbox diagonal
SYMMETRY_GRID = 64             # occupancy grid resolution for symmetry tests
SYMMETRY_AXES = 12            # candidate mirror axes
SYMMETRY_ORDERS = (2, 3, 4, 5, 6, 8, 12)
SYMMETRY_TOLERANCE = 0.80      # overlap fraction that counts as symmetric
HOLE_MIN_AREA_RATIO = 0.002    # ignore counters smaller than this share of ink
MIN_COMPONENT_AREA = 12        # raster component area floor, pixels
MIN_TECHNIQUE_SCORE = 0.20     # below this a technique is not reported at all
MIN_SUPPORT_SCORE = 0.35       # supporting gestures need at least this
CONFIDENCE_FLOOR = 0.55        # below this, apply the global haircut

# Scenario ids, taken from references/taxonomy.md so a recommendation is
# expressible in the existing brief and manifest vocabulary.
SCENARIO_IDS = {
    "line_draw_on": "LINE-01",
    "multi_stroke_trace": "LINE-02",
    "kinetic_typography": "KINE-01",
    "mask_wipe": "WORD-02",
    "mask_wipe_mark": "GEO-01",
    "circular_sweep": "BADGE-01",
    "particle_dissolve": "FX-02",
    "morph_shape": "GEO-03",
    "separation_explode": "SEP-01",
    "separation_ordered": "SEP-04",
    "geometric_construction": "GEO-02",
    "extrusion_3d": "SEP-03",
    "bounce_elastic": "PLAY-01",
    "orbit_rotate": "IDLE-02",
    "orbit_rotate_badge": "BADGE-03",
    "gradient_sweep": "PREM-03",
    "idle_loop": "IDLE-01",
    "scroll_scrub": "IDLE-04",
}

TECHNIQUE_ROLES = {
    "line_draw_on": "reveal",
    "kinetic_typography": "reveal",
    "mask_wipe": "reveal",
    "circular_sweep": "reveal",
    "particle_dissolve": "reveal",
    "morph_shape": "reveal",
    "separation_explode": "transform",
    "separation_ordered": "transform",
    "geometric_construction": "transform",
    "extrusion_3d": "transform",
    "bounce_elastic": "transform",
    "gradient_sweep": "surface",
    "orbit_rotate": "loop",
    "idle_loop": "loop",
    "scroll_scrub": "driver",
    "reduced_motion": "a11y",
}

# Capability ladder, references/technique-selection.md.
RUNG_FAMILIES = {
    0: ["whole-mark fade", "mask wipe", "split", "filter"],
    1: ["whole-mark fade", "mask wipe", "split", "filter", "circular sweep"],
    2: ["line drawing", "mask wipe", "circular sweep", "morph"],
    3: ["separation", "choreography", "kinetic typography", "geometric construction"],
    4: ["junction handling", "draw-then-fill", "line drawing", "travelling dash"],
    5: ["matter effects", "gradient sweep", "mask work"],
    6: ["per-glyph choreography", "contour trace", "kinetic typography"],
    7: ["variable-axis typography", "text on a path"],
    8: ["interactive states", "state machines", "scroll scrub"],
}


# --------------------------------------------------------------------------
# SVG path parsing and measurement. Standard library only.
# --------------------------------------------------------------------------

COMMAND_RE = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])")
NUMBER_RE = re.compile(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")
ARC_PARAMS = {"A": 7, "a": 7}
SEGMENT_PARAMS = {"L": 2, "l": 2, "H": 1, "h": 1, "V": 1, "v": 1,
                  "C": 6, "c": 6, "S": 4, "s": 4, "Q": 4, "q": 4, "T": 2, "t": 2}


def tokenize_path(d: str):
    """Yield (command, [numbers]) tuples from an SVG path data string."""
    tokens = COMMAND_RE.split(d or "")
    index = 1
    while index < len(tokens):
        command = tokens[index].strip()
        if not command:
            index += 1
            continue
        payload = tokens[index + 1] if index + 1 < len(tokens) else ""
        numbers = [float(value) for value in NUMBER_RE.findall(payload)]
        yield command, numbers
        index += 2


def _cubic_point(p0, p1, p2, p3, t):
    mt = 1.0 - t
    a, b, c, e = mt * mt * mt, 3 * mt * mt * t, 3 * mt * t * t, t * t * t
    return (a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0],
            a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1])


def _quadratic_point(p0, p1, p2, t):
    mt = 1.0 - t
    a, b, c = mt * mt, 2 * mt * t, t * t
    return (a * p0[0] + b * p1[0] + c * p2[0],
            a * p0[1] + b * p1[1] + c * p2[1])


def _arc_point(p0, rx, ry, rotation, large_arc, sweep, p1, t):
    """Endpoint-parameterised elliptical arc, flattened to a point at t."""
    if rx == 0 or ry == 0 or (abs(p0[0] - p1[0]) < EPS and abs(p0[1] - p1[1]) < EPS):
        return (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(rotation % 360.0)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)
    dx2, dy2 = (p0[0] - p1[0]) / 2.0, (p0[1] - p1[1]) / 2.0
    x1 = cos_phi * dx2 + sin_phi * dy2
    y1 = -sin_phi * dx2 + cos_phi * dy2
    lam = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if lam > 1.0:
        scale = math.sqrt(lam)
        rx, ry = rx * scale, ry * scale
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    factor = math.sqrt(max(num / den, 0.0)) if den else 0.0
    if bool(large_arc) == bool(sweep):
        factor = -factor
    cx1 = factor * rx * y1 / ry
    cy1 = -factor * ry * x1 / rx
    cx = cos_phi * cx1 - sin_phi * cy1 + (p0[0] + p1[0]) / 2.0
    cy = sin_phi * cx1 + cos_phi * cy1 + (p0[1] + p1[1]) / 2.0
    theta = math.atan2((y1 - cy1) / ry, (x1 - cx1) / rx)
    delta = math.atan2((-y1 - cy1) / ry, (-x1 - cx1) / rx) - theta
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi
    angle = theta + delta * t
    return (cx + rx * math.cos(angle) * cos_phi - ry * math.sin(angle) * sin_phi,
            cy + rx * math.cos(angle) * sin_phi + ry * math.sin(angle) * cos_phi)


def measure_subpaths(d: str) -> list[dict]:
    """Split a path data string into subpaths and measure each one.

    Returns one record per author subpath with its flattened point list,
    polyline length, closedness, and segment count. Closedness is reported
    twice on purpose: `author_closed` is the presence of a Z command, which is
    what decides join-versus-cap behaviour at the seam, and `geometric_closed`
    is whether the endpoints coincide.
    """
    subpaths: list[dict] = []
    current: dict | None = None
    point = (0.0, 0.0)
    start = (0.0, 0.0)
    last_control: tuple[float, float] | None = None
    last_command = ""

    def ensure():
        nonlocal current
        if current is None:
            current = {"points": [point], "length": 0.0, "segments": 0,
                       "anchors": 1, "author_closed": False, "geometric_closed": False}
            subpaths.append(current)
        return current

    for command, numbers in tokenize_path(d):
        if command in ("M", "m"):
            if not numbers:
                continue
            relative = command == "m"
            if len(numbers) >= 2:
                x, y = numbers[0], numbers[1]
                point = (point[0] + x, point[1] + y) if relative else (x, y)
            start = point
            current = {"points": [point], "length": 0.0, "segments": 0,
                       "anchors": 1, "author_closed": False, "geometric_closed": False}
            subpaths.append(current)
            index = 2
            while index + 1 < len(numbers):
                x, y = numbers[index], numbers[index + 1]
                nxt = (point[0] + x, point[1] + y) if relative else (x, y)
                record = ensure()
                record["length"] += math.dist(point, nxt)
                record["points"].append(nxt)
                record["segments"] += 1
                record["anchors"] += 1
                point = nxt
                index += 2
            last_control, last_command = None, "M"
            continue

        record = ensure()
        if command in ("Z", "z"):
            record["author_closed"] = True
            if math.dist(point, start) > EPS:
                record["length"] += math.dist(point, start)
                record["points"].append(start)
            point = start
            last_control, last_command = None, "Z"
            continue

        expected = SEGMENT_PARAMS.get(command, ARC_PARAMS.get(command, 0))
        if not expected:
            continue
        index = 0
        while index + expected <= len(numbers):
            args = numbers[index:index + expected]
            index += expected
            upper = command.upper()
            relative = command.islower()
            ox, oy = point
            if upper == "L":
                target = (ox + args[0], oy + args[1]) if relative else (args[0], args[1])
                record["length"] += math.dist(point, target)
                record["points"].append(target)
                last_control = None
            elif upper == "H":
                target = ((ox + args[0]) if relative else args[0], oy)
                record["length"] += math.dist(point, target)
                record["points"].append(target)
                last_control = None
            elif upper == "V":
                target = (ox, (oy + args[0]) if relative else args[0])
                record["length"] += math.dist(point, target)
                record["points"].append(target)
                last_control = None
            elif upper in ("C", "S"):
                if upper == "C":
                    c1 = (ox + args[0], oy + args[1]) if relative else (args[0], args[1])
                    c2 = (ox + args[2], oy + args[3]) if relative else (args[2], args[3])
                    target = (ox + args[4], oy + args[5]) if relative else (args[4], args[5])
                else:
                    if last_command in ("C", "S") and last_control:
                        c1 = (2 * ox - last_control[0], 2 * oy - last_control[1])
                    else:
                        c1 = point
                    c2 = (ox + args[0], oy + args[1]) if relative else (args[0], args[1])
                    target = (ox + args[2], oy + args[3]) if relative else (args[2], args[3])
                for step in range(1, FLATTEN_SEGMENTS + 1):
                    sample = _cubic_point(point, c1, c2, target, step / FLATTEN_SEGMENTS)
                    record["length"] += math.dist(record["points"][-1], sample)
                    record["points"].append(sample)
                last_control = c2
            elif upper in ("Q", "T"):
                if upper == "Q":
                    c1 = (ox + args[0], oy + args[1]) if relative else (args[0], args[1])
                    target = (ox + args[2], oy + args[3]) if relative else (args[2], args[3])
                else:
                    if last_command in ("Q", "T") and last_control:
                        c1 = (2 * ox - last_control[0], 2 * oy - last_control[1])
                    else:
                        c1 = point
                    target = (ox + args[0], oy + args[1]) if relative else (args[0], args[1])
                for step in range(1, FLATTEN_SEGMENTS + 1):
                    sample = _quadratic_point(point, c1, target, step / FLATTEN_SEGMENTS)
                    record["length"] += math.dist(record["points"][-1], sample)
                    record["points"].append(sample)
                last_control = c1
            elif upper == "A":
                rx, ry, rot = args[0], args[1], args[2]
                large_arc, sweep = bool(args[3]), bool(args[4])
                target = (ox + args[5], oy + args[6]) if relative else (args[5], args[6])
                for step in range(1, FLATTEN_SEGMENTS + 1):
                    sample = _arc_point(point, rx, ry, rot, large_arc, sweep,
                                        target, step / FLATTEN_SEGMENTS)
                    record["length"] += math.dist(record["points"][-1], sample)
                    record["points"].append(sample)
                last_control = None
            record["segments"] += 1
            record["anchors"] += 1
            point = target
            last_command = upper

    for record in subpaths:
        if len(record["points"]) >= 2:
            record["geometric_closed"] = math.dist(record["points"][0], record["points"][-1]) <= EPS
    return subpaths


def polygon_area(points) -> float:
    total = 0.0
    for index in range(len(points)):
        x0, y0 = points[index]
        x1, y1 = points[(index + 1) % len(points)]
        total += x0 * y1 - x1 * y0
    return total / 2.0


def convex_hull(points) -> list:
    unique = sorted(set((round(x, 6), round(y, 6)) for x, y in points))
    if len(unique) < 3:
        return unique

    def half(seq):
        stack = []
        for point in seq:
            while len(stack) >= 2:
                (ax, ay), (bx, by) = stack[-2], stack[-1]
                if (bx - ax) * (point[1] - ay) - (by - ay) * (point[0] - ax) > 0:
                    break
                stack.pop()
            stack.append(point)
        return stack

    lower = half(unique)
    upper = half(reversed(unique))
    return lower[:-1] + upper[:-1]


# --------------------------------------------------------------------------
# Symmetry on an occupancy grid. Deterministic, standard library only.
# --------------------------------------------------------------------------

def _occupancy(points, size: int) -> set:
    if not points:
        return set()
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    width = max(max(xs) - min(xs), EPS)
    height = max(max(ys) - min(ys), EPS)
    span = max(width, height)
    cells = set()
    for x, y in points:
        col = int((x - min(xs)) / span * (size - 1))
        row = int((y - min(ys)) / span * (size - 1))
        cells.add((col, row))
    return cells


def _overlap(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a | b), 1)


def symmetry_scores(points) -> dict:
    if len(points) < 8:
        return {"sym_mirror": 0.0, "sym_mirror_axis": 0.0,
                "sym_rot_k": 1, "sym_rot_score": 0.0, "sym_ambiguous": True}
    base = _occupancy(points, SYMMETRY_GRID)
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)

    best_axis, best_mirror, baseline = 0.0, 0.0, 0.0
    axis_scores = []
    for step in range(SYMMETRY_AXES):
        angle = math.pi * step / SYMMETRY_AXES
        ux, uy = math.cos(angle), math.sin(angle)
        reflected = set()
        for col, row in base:
            x, y = col / (SYMMETRY_GRID - 1), row / (SYMMETRY_GRID - 1)
            dx, dy = x - 0.5, y - 0.5
            dot = dx * ux + dy * uy
            rx, ry = 2 * dot * ux - dx, 2 * dot * uy - dy
            reflected.add((int(round((rx + 0.5) * (SYMMETRY_GRID - 1))),
                           int(round((ry + 0.5) * (SYMMETRY_GRID - 1)))))
        score = _overlap(base, reflected)
        axis_scores.append(score)
        baseline += score
        if score > best_mirror:
            best_mirror, best_axis = score, math.degrees(angle)
    baseline /= max(len(axis_scores), 1)

    best_k, best_rot = 1, 0.0
    for order in SYMMETRY_ORDERS:
        theta = 2 * math.pi / order
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        rotated = set()
        for col, row in base:
            x, y = col / (SYMMETRY_GRID - 1) - 0.5, row / (SYMMETRY_GRID - 1) - 0.5
            rx = x * cos_t - y * sin_t
            ry = x * sin_t + y * cos_t
            rotated.add((int(round((rx + 0.5) * (SYMMETRY_GRID - 1))),
                         int(round((ry + 0.5) * (SYMMETRY_GRID - 1)))))
        score = _overlap(base, rotated)
        if score > best_rot:
            best_k, best_rot = order, score

    return {
        "sym_mirror": round(best_mirror, 3),
        "sym_mirror_axis": round(best_axis, 1),
        "sym_rot_k": best_k,
        "sym_rot_score": round(best_rot, 3),
        "sym_discriminative": round(max(best_mirror - baseline, 0.0), 3),
        "sym_ambiguous": best_mirror < SYMMETRY_TOLERANCE and best_rot < SYMMETRY_TOLERANCE,
        "_centroid": [round(cx, 4), round(cy, 4)],
    }


# --------------------------------------------------------------------------
# Vector profiling
# --------------------------------------------------------------------------

def _local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _style_of(element) -> dict:
    style = {}
    for key, value in element.attrib.items():
        name = _local(key)
        if name == "style":
            for declaration in value.split(";"):
                if ":" in declaration:
                    prop, _, val = declaration.partition(":")
                    style[prop.strip()] = val.strip()
        else:
            style[name] = value
    return style


def _inherited_fill_rules(element, inherited: dict) -> dict:
    style = dict(inherited)
    style.update(_style_of(element))
    return style


def _is_paint(value) -> bool:
    return bool(value) and value.strip().lower() not in {"none", "transparent"}


def profile_svg(path: Path) -> dict:
    """Structural fingerprint of an SVG. Standard library only."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise RuntimeError(f"Could not parse {path} as SVG: {exc}") from exc
    root = tree.getroot()

    census: dict[str, int] = {}
    subpaths: list[dict] = []
    path_data: list[str] = []
    stroke_widths: list[float] = []
    line_caps: dict[str, int] = {}
    fills = 0
    stroke_present = False
    text_nodes = 0
    gradient_count = 0
    filter_count = mask_count = clip_count = 0
    use_count = 0
    group_depth_max = 0
    translate_only_groups = 0
    fill_rules: dict[str, int] = {}
    duplicate_clusters: dict[str, int] = {}
    declared_ids = set()
    referenced_ids: list[str] = []
    semantic_hits: list[str] = []
    dash_present = False
    named_parts: list[str] = []
    semantic_lexicon = {
        "wordmark": ("word", "text", "logotype", "lettering", "caption"),
        "lettermark": ("mono", "initial", "lettermark", "firstletter"),
        "symbol": ("symbol", "mark", "emblem", "badge", "icon", "mascot"),
        "container": ("plate", "frame", "bg", "background", "shield", "ring", "circle"),
        "accent": ("accent", "shine", "gloss", "gradient", "sparkle"),
    }

    def walk(element, depth: int, inherited: dict):
        nonlocal stroke_present, fills, text_nodes, gradient_count, filter_count
        nonlocal mask_count, clip_count, use_count, group_depth_max
        nonlocal translate_only_groups, dash_present, named_parts
        tag = _local(element.tag)
        census[tag] = census.get(tag, 0) + 1
        if tag in {"defs", "title", "desc", "metadata", "style"}:
            return
        if tag in {"linearGradient", "radialGradient", "pattern"}:
            gradient_count += 1
            return
        if tag == "filter":
            filter_count += 1
            return
        if tag == "mask":
            mask_count += 1
            return
        if tag == "clipPath":
            clip_count += 1
            return
        identifier = element.get("id")
        if identifier:
            declared_ids.add(identifier)
        for key in ("id", "class", "aria-label", "data-name", "label"):
            value = (element.get(key) or "").lower()
            if value:
                for name, needles in semantic_lexicon.items():
                    if any(needle in value for needle in needles):
                        semantic_hits.append(name)
        href = element.get("href") or element.get(
            "{http://www.w3.org/1999/xlink}href")
        if tag in {"use", "textPath"} and href and href.startswith("#"):
            use_count += 1
            referenced_ids.append(href[1:])

        style = _inherited_fill_rules(element, inherited)
        if _is_paint(style.get("fill")):
            fills += 1
            fill_rules[style.get("fill-rule", "nonzero")] = \
                fill_rules.get(style.get("fill-rule", "nonzero"), 0) + 1
        if _is_paint(style.get("stroke")):
            stroke_present = True
            try:
                stroke_widths.append(float(re.sub(r"[a-z%]+$", "", str(style.get("stroke-width", "1")))))
            except ValueError:
                stroke_widths.append(1.0)
            line_caps[style.get("stroke-linecap", "butt")] = \
                line_caps.get(style.get("stroke-linecap", "butt"), 0) + 1
            if style.get("stroke-dasharray") not in (None, "none"):
                dash_present = True

        if tag == "text":
            text_nodes += 1
        if tag in {"path", "line", "polyline", "polygon", "rect", "circle", "ellipse"}:
            if identifier:
                named_parts.append(identifier)
            data = style.get("d")
            if data:
                normalized = re.sub(r"[\s,]+", " ", data.strip())
                duplicate_clusters[normalized] = duplicate_clusters.get(normalized, 0) + 1
                path_data.append(data)
                try:
                    for record in measure_subpaths(data):
                        record["stroked"] = _is_paint(style.get("stroke"))
                        subpaths.append(record)
                except Exception:  # a malformed path must not lose the whole file
                    pass
            else:
                # Primitives become a closed subpath in intent even without a d.
                box = _primitive_box(tag, style)
                if box:
                    x0, y0, x1, y1 = box
                    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
                    subpaths.append({
                        "points": ring,
                        "length": 2 * ((x1 - x0) + (y1 - y0)),
                        "segments": 4,
                        "anchors": 4,
                        "author_closed": True,
                        "geometric_closed": True,
                        "stroked": _is_paint(style.get("stroke")),
                        "primitive": tag,
                    })
        if tag == "g":
            group_depth_max = max(group_depth_max, depth)
            transform = (element.get("transform") or "").lower()
            if transform and "translate" in transform and \
                    "rotate" not in transform and "scale" not in transform:
                translate_only_groups += 1
        for child in element:
            walk(child, depth + 1, style)

    walk(root, 0, {"fill": "black"})

    points = [point for record in subpaths for point in record["points"]]
    if not points:
        raise RuntimeError(
            f"{path} contains no drawable geometry; profiling cannot infer motion "
            "from a file with no shapes.")
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    width = max(bbox[2] - bbox[0], EPS)
    height = max(bbox[3] - bbox[1], EPS)
    diagonal = math.hypot(width, height)

    total_length = sum(record["length"] for record in subpaths) or EPS
    open_length = sum(record["length"] for record in subpaths if not record["author_closed"])
    open_subpaths = [record for record in subpaths if not record["author_closed"]]
    closed_subpaths = [record for record in subpaths if record["author_closed"]]
    nodes = sum(max(record.get("anchors", record["segments"]), 1) for record in subpaths)

    rings = [record["points"] for record in closed_subpaths
             if abs(polygon_area(record["points"])) > HOLE_MIN_AREA_RATIO * width * height]
    ink_area = sum(abs(polygon_area(ring)) for ring in rings) or EPS
    part_areas = sorted((abs(polygon_area(record["points"])) for record in subpaths), reverse=True)
    part_areas = [value for value in part_areas if value > HOLE_MIN_AREA_RATIO * width * height]
    total_parts = sum(part_areas)
    part_max_share = part_areas[0] / total_parts if total_parts > EPS else 1.0
    part_entropy = 0.0
    denominator = math.log2(len(part_areas) + 1)
    if len(part_areas) > 1 and denominator > EPS and total_parts > EPS:
        for value in part_areas:
            share = value / total_parts
            if share > 0:
                part_entropy -= share * math.log2(share)
        part_entropy /= denominator
    # Ink coverage: filled rings plus the area a stroke lays down, so a
    # monoline mark does not report as an empty silhouette.
    median_stroke = sorted(stroke_widths)[len(stroke_widths) // 2] if stroke_widths else 0.0
    stroked_length = sum(record["length"] for record in subpaths if record.get("stroked"))
    ink_estimate = ink_area + stroked_length * max(median_stroke, 0.0)
    hull_area = abs(polygon_area(convex_hull(points))) or EPS
    hole_count, hole_area = _count_holes(rings, width * height)

    edge_lengths = [math.dist(a, b) for record in subpaths
                    for a, b in zip(record["points"], record["points"][1:])]
    mean_edge = sum(edge_lengths) / len(edge_lengths) if edge_lengths else 0.0
    variance = (sum((value - mean_edge) ** 2 for value in edge_lengths) / len(edge_lengths)
                if edge_lengths else 0.0)
    edge_cv = math.sqrt(variance) / mean_edge if mean_edge > EPS else 0.0

    turning = 0.0
    corners = 0
    joints = 0
    for record in subpaths:
        pts = record["points"]
        for index in range(1, len(pts) - 1):
            ax, ay = pts[index - 1]
            bx, by = pts[index]
            cx, cy = pts[index + 1]
            v1 = (bx - ax, by - ay)
            v2 = (cx - bx, cy - by)
            n1 = math.hypot(*v1)
            n2 = math.hypot(*v2)
            if n1 < EPS or n2 < EPS:
                continue
            cosine = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
            angle = math.degrees(math.acos(cosine))
            turning += angle
            joints += 1
            if angle > 40.0:
                corners += 1

    characteristic = math.sqrt(width * height)
    vertex_density = nodes * characteristic / total_length
    solidity = min(ink_area / hull_area, 1.0)
    aspect = max(width, height) / max(min(width, height), EPS)
    asympect = (width - height) / diagonal
    perimeter = total_length
    circularity = 4 * math.pi * ink_area / (perimeter * perimeter) if perimeter > EPS else 0.0

    symmetry = symmetry_scores(points)
    complexity, complexity_band = _complexity(
        vertex_density=vertex_density,
        turning=turning,
        solidity=solidity,
        hole_count=hole_count,
        hole_area_ratio=hole_area / ink_area,
        nodes=nodes,
        edge_cv=edge_cv,
        corner_share=corners / joints if joints else 0.0,
        gradient_count=gradient_count,
        color_count=1,
        parts=max(len(named_parts), 1),
    )

    centroid = _ink_centroid(subpaths)
    centroid_offset = math.dist(centroid, [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]) / diagonal

    return {
        "kind": "svg",
        "bbox": [round(value, 4) for value in bbox],
        "aspect": round(aspect, 3),
        "aspect_signed": round(asympect, 3),
        "part_max_share": round(part_max_share, 4),
        "part_entropy": round(part_entropy, 4),
        "named_part_count": len(named_parts),
        "named_parts": named_parts[:24],
        "component_count": len(named_parts),
        "component_note": "for a vector source this counts individually addressable named "
                          "parts, not pixel components; it is evidence of separable layers, "
                          "not a guarantee of non-overlap",
        "shape_count": census.get("path", 0) + census.get("circle", 0) + census.get("rect", 0)
                       + census.get("polygon", 0) + census.get("polyline", 0)
                       + census.get("ellipse", 0) + census.get("line", 0),
        "path_count": census.get("path", 0),
        "subpath_count": len(subpaths),
        "open_subpath_count": len(open_subpaths),
        "closed_subpath_count": len(closed_subpaths),
        "open_len_ratio": round(open_length / total_length, 4),
        "total_length": round(total_length, 4),
        "nodes_total": nodes,
        "stroke_present": stroke_present,
        "stroke_width_norm": round((sorted(stroke_widths)[len(stroke_widths) // 2] / diagonal), 5)
                             if stroke_widths else 0.0,
        "stroke_width_cv": round(edge_cv, 4),
        "stroke_size_ratio": round(_stroke_size_ratio(stroke_widths, diagonal), 5),
        "line_caps": line_caps,
        "dash_present": dash_present,
        "fill_present": fills > 0,
        "hole_count": hole_count,
        "hole_area_ratio": round(hole_area / ink_area, 4),
        "text_present": text_nodes > 0,
        "text_count": text_nodes,
        "text_outlined": text_nodes == 0,
        "gradient_count": gradient_count,
        "filter_count": filter_count,
        "mask_count": mask_count,
        "clip_count": clip_count,
        "color_count": 1 + gradient_count,
        "group_depth_max": group_depth_max,
        "translate_only_groups": translate_only_groups,
        "use_count": use_count,
        "missing_targets": sorted({name for name in referenced_ids if name not in declared_ids}),
        "duplicate_clusters": sum(1 for count in duplicate_clusters.values() if count > 1),
        "duplicate_instance_count": sum(count for count in duplicate_clusters.values() if count > 1),
        "semantic_layer_hits": sorted(set(semantic_hits)),
        "fill_rules": fill_rules,
        "complexity": complexity,
        "complexity_band": complexity_band,
        "solidity": round(solidity, 4),
        "circularity": round(circularity, 4),
        "vertex_density": round(vertex_density, 3),
        "corner_share": round(corners / joints, 4) if joints else 0.0,
        "total_turning_deg": round(turning, 2),
        "centroid": [round(centroid[0], 4), round(centroid[1], 4)],
        "centroid_offset": round(centroid_offset, 4),
        "ink_ratio": round(min(ink_estimate / (width * height), 1.0), 4),
        **{key: value for key, value in symmetry.items() if not key.startswith("_")},
        "geometry_fidelity": "authored",
        "style_resolution": "full",
    }


def _primitive_box(tag: str, style: dict):
    def number(name, default=0.0):
        raw = re.sub(r"[a-z%]+$", "", str(style.get(name, default)))
        try:
            return float(raw)
        except ValueError:
            return float(default)

    if tag == "rect":
        x, y, w, h = number("x"), number("y"), number("width"), number("height")
        if w > EPS and h > EPS:
            return (x, y, x + w, y + h)
    elif tag == "circle":
        cx, cy, r = number("cx"), number("cy"), number("r")
        if r > EPS:
            return (cx - r, cy - r, cx + r, cy + r)
    elif tag == "ellipse":
        cx, cy, rx, ry = number("cx"), number("cy"), number("rx"), number("ry")
        if rx > EPS and ry > EPS:
            return (cx - rx, cy - ry, cx + rx, cy + ry)
    return None


def _count_holes(rings, canvas_area) -> tuple[int, float]:
    """Count rings fully contained by another ring, honouring winding sign."""
    if not rings:
        return 0, 0.0
    areas = [abs(polygon_area(ring)) for ring in rings]
    total = sum(areas) or EPS
    holes = 0
    hole_area = 0.0
    for index, ring in enumerate(rings):
        if areas[index] <= HOLE_MIN_AREA_RATIO * canvas_area:
            continue
        probe = ring[len(ring) // 2]
        contained = 0
        for other_index, other in enumerate(rings):
            if other_index == index or areas[other_index] <= areas[index]:
                continue
            if _point_in_ring(probe, other):
                contained += 1
        if contained and (contained % 2 == 1 or math.copysign(1, polygon_area(ring))
                          != math.copysign(1, polygon_area(rings[0]))):
            holes += 1
            hole_area += areas[index]
    return holes, min(hole_area, total)


def _point_in_ring(point, ring) -> bool:
    x, y = point
    inside = False
    for index in range(len(ring) - 1):
        x0, y0 = ring[index]
        x1, y1 = ring[index + 1]
        if (y0 > y) != (y1 > y):
            t = (y - y0) / (y1 - y0) if abs(y1 - y0) > EPS else 0.0
            if x < x0 + t * (x1 - x0):
                inside = not inside
    return inside


def _ink_centroid(subpaths) -> tuple:
    weighted_x = weighted_y = weight = 0.0
    for record in subpaths:
        pts = record["points"]
        if len(pts) < 3:
            continue
        area = polygon_area(pts)
        if abs(area) < EPS:
            continue
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        mass = abs(area)
        weighted_x += cx * mass
        weighted_y += cy * mass
        weight += mass
    if weight < EPS:
        return (0.0, 0.0)
    return (weighted_x / weight, weighted_y / weight)


def _stroke_size_ratio(widths, diagonal) -> float:
    if not widths:
        return 0.0
    ordered = sorted(widths)
    return ordered[len(ordered) // 2] / max(diagonal, EPS)


def _complexity(**metrics) -> tuple:
    def ramp(value, low, high):
        if value <= low:
            return 0.0
        if value >= high:
            return 1.0
        return (value - low) / (high - low)

    weights = {
        "vertex_density": 0.16, "turning": 0.12, "nonconvexity": 0.12,
        "holes": 0.10, "nodes": 0.12, "edge_cv": 0.06, "corners": 0.06,
        "paint": 0.08, "parts": 0.18,
    }
    parts = {
        "vertex_density": ramp(metrics["vertex_density"], 2, 40),
        "turning": ramp(metrics["turning"] / 360.0, 1.15, 3.2),
        "nonconvexity": ramp(1.0 - metrics["solidity"], 0.05, 0.55),
        "holes": ramp(metrics["hole_count"] + 3 * metrics["hole_area_ratio"], 0.5, 8.0),
        "nodes": ramp(metrics["nodes"], 4, 150),
        "parts": ramp(metrics["parts"], 1, 9),
        "edge_cv": ramp(metrics["edge_cv"], 0.25, 1.6),
        "corners": ramp(metrics["corner_share"], 0.05, 0.45),
        "paint": ramp(0.6 * ramp(metrics["color_count"], 2, 64)
                      + 0.4 * ramp(metrics["gradient_count"], 0, 3), 0.0, 0.8),
    }
    score = round(100 * sum(weights[key] * parts[key] for key in weights), 1)
    band = ("atomic" if score < 20 else "geometric" if score < 38 else
            "moderate" if score < 55 else "detailed" if score < 72 else "illustrative")
    return score, band


# --------------------------------------------------------------------------
# Raster profiling. Optional dependencies, reported honestly when missing.
# --------------------------------------------------------------------------

def profile_raster(path: Path) -> dict:
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return {"kind": "raster-unavailable",
                "warnings": ["Pillow and NumPy are required to profile a raster source."]}

    warnings: list[str] = []
    try:
        image = Image.open(path)
        image.load()
    except Exception as exc:
        raise RuntimeError(f"Could not read {path}: {exc}") from exc

    rgba = np.asarray(image.convert("RGBA"))
    alpha = rgba[:, :, 3]
    ink = alpha > 16
    total_px = ink.size
    ink_pixels = int(ink.sum())
    profile: dict = {
        "kind": "raster",
        "width": image.width,
        "height": image.height,
        "format": image.format,
        "ink_ratio": round(ink_pixels / total_px, 4),
        "color_count": 0,
        "alpha_levels": int(np.unique(alpha).size),
        "gradient_area_ratio": 0.0,
        "component_count": 0,
        "all_disjoint": None,
        "component_max_share": 1.0,
        "component_entropy": 0.0,
        "hole_count": 0,
        "stroke_size_ratio": 0.0,
        "edge_density": 0.0,
        "sym_rot_k": 1,
        "sym_mirror": 0.0,
        "geometry_fidelity": "raster",
        "style_resolution": "full",
        "warnings": warnings,
    }
    if ink_pixels == 0:
        warnings.append("No visible alpha pixels; nothing to profile.")
        return profile

    ys, xs = np.nonzero(ink)
    profile["bbox"] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    width = max(int(xs.max() - xs.min()), 1)
    height = max(int(ys.max() - ys.min()), 1)
    diagonal = math.hypot(width, height)
    profile["aspect"] = round(max(width, height) / max(min(width, height), 1), 3)
    profile["aspect_signed"] = round((width - height) / diagonal, 3)

    colors = rgba[..., :3][ink]
    if colors.size:
        quantized = (colors // 32).astype(np.int32)
        packed = quantized[:, 0] * 1024 + quantized[:, 1] * 32 + quantized[:, 2]
        profile["color_count"] = int(np.unique(packed).size)
        counts = np.bincount(packed.ravel())
        shares = counts[counts > 0] / counts.sum()
        profile["flat"] = bool(profile["color_count"] <= 3)
        profile["color_entropy"] = round(float(-(shares * np.log2(shares)).sum() / math.log2(len(shares) + 1)), 4)

    # Hole detection by flooding the background from the frame edge.
    padded = np.pad(ink, 1, constant_values=False)
    background = ~padded
    try:
        from scipy import ndimage
        labels, count = ndimage.label(background)
        edge_labels = set(np.unique(labels[0, :])) | set(np.unique(labels[-1, :])) \
            | set(np.unique(labels[:, 0])) | set(np.unique(labels[:, -1]))
        hole_labels = [label for label in np.unique(labels) if label and label not in edge_labels]
        hole_pixels = 0
        for label in hole_labels:
            selection = labels == label
            area = int(selection.sum())
            if area >= HOLE_MIN_AREA_RATIO * ink_pixels:
                hole_pixels += area
        profile["hole_count"] = len(hole_labels)
        profile["hole_area_ratio"] = round(hole_pixels / ink_pixels, 4)
    except ImportError:
        warnings.append("SciPy is unavailable; hole and component metrics were skipped.")
        ndimage = None

    if ndimage is not None:
        labels, count = ndimage.label(ink, structure=np.ones((3, 3), dtype=int))
        sizes = ndimage.sum(ink, labels, index=np.arange(1, count + 1))
        keep = [index + 1 for index, size in enumerate(sizes) if size >= MIN_COMPONENT_AREA]
        profile["component_count"] = int(count)
        profile["component_reported"] = len(keep)
        if keep:
            ordered = sorted(keep, key=lambda label: -ndimage.sum(ink, labels, label))
            shares = [float(ndimage.sum(ink, labels, label)) / ink_pixels for label in ordered]
            profile["component_max_share"] = round(shares[0], 4)
            total = sum(shares)
            profile["component_entropy"] = round(
                float(-sum(s * math.log2(s) for s in shares if s > 0) / math.log2(len(shares) + 1)), 4)
            collisions = 0
            for label in ordered[:24]:
                mask = (labels == label)
                ring = mask & ~ndimage.binary_erosion(mask, structure=np.ones((3, 3)))
                touching = set(np.unique(labels[ring])) - {0, label}
                if touching:
                    collisions += 1
            profile["all_disjoint"] = collisions == 0
            boxes = []
            for label in ordered[:24]:
                where = np.nonzero(labels == label)
                boxes.append([int(where[1].min()), int(where[0].min()),
                              int(where[1].max()), int(where[0].max())])
            profile["component_boxes"] = boxes
            if len(ordered) >= 2 and boxes:
                tops = [box[1] for box in boxes]
                bottoms = [box[3] for box in boxes]
                heights = [b - t for t, b in zip(tops, bottoms) if b > t]
                if heights:
                    mean_h = sum(heights) / len(heights)
                    profile["uniform_component_height"] = bool(
                        all(abs(value - mean_h) <= 0.25 * mean_h for value in heights))
        distance = ndimage.distance_transform_edt(ink)
        skeleton_sizes = sizes
        if len(skeleton_sizes):
            interior = distance[distance > 0]
            if interior.size:
                profile["stroke_size_ratio"] = round(
                    float(np.percentile(interior, 90)) * 2 / max(diagonal, 1), 5)
        edges = np.zeros(ink.shape, dtype=bool)
        edges[:, :-1] |= ink[:, :-1] != ink[:, 1:]
        edges[:-1, :] |= ink[:-1, :] != ink[1:, :]
        profile["edge_density"] = round(float((edges & ink).sum()) / max(ink_pixels, 1), 4)

    if profile["alpha_levels"] >= 50:
        profile["geometry_fidelity"] = "raster"
        profile["flattened_evidence"] = True
    symmetry = symmetry_scores([(float(x), float(y)) for x, y in
                                zip(np.nonzero(ink)[1][::7], np.nonzero(ink)[0][::7])])
    for key, value in symmetry.items():
        if not key.startswith("_"):
            profile[key] = value

    profile["complexity"], profile["complexity_band"] = _complexity(
        vertex_density=profile.get("edge_density", 0.0) * 40,
        turning=1.0,
        solidity=0.75,
        hole_count=profile.get("hole_count", 0),
        hole_area_ratio=profile.get("hole_area_ratio", 0.0),
        nodes=profile.get("component_count", 0) * 20,
        edge_cv=0.6,
        corner_share=0.2,
        gradient_count=1 if profile.get("gradient_area_ratio", 0) > 0.15 else 0,
        color_count=profile.get("color_count", 1),
        parts=max(int(profile.get("component_count") or 1), 1),
    )
    warnings.append(
        "Connected components are diagnostic evidence, not guaranteed semantic logo layers.")
    return profile


# --------------------------------------------------------------------------
# Capability, gates, rules
# --------------------------------------------------------------------------

def capability_rung(profile: dict) -> tuple[int, list]:
    if profile.get("kind") == "raster":
        has_layers = (profile.get("component_count") or 0) >= 2
        rung = 3 if has_layers else 0
        return rung, list(RUNG_FAMILIES[rung])
    rung = 2
    if profile.get("subpath_count", 0) >= 2 or profile.get("group_depth_max", 0) > 0:
        rung = 3
    if profile.get("stroke_present"):
        rung = 4
    if profile.get("gradient_count") or profile.get("mask_count") or profile.get("clip_count") \
            or profile.get("filter_count"):
        rung = 5
    if profile.get("text_present"):
        rung = 7
    elif profile.get("shape_count", 0) >= 4 and not profile.get("text_present"):
        rung = max(rung, 6) if profile.get("hole_count", 0) >= 1 else rung
    return rung, list(RUNG_FAMILIES[min(rung, 8)])


def feasibility_gates(profile: dict) -> dict:
    gates: dict[str, list] = {}
    rung, _ = capability_rung(profile)

    def block(technique, code, detail, remedy=None):
        gates.setdefault(technique, []).append(
            {"code": code, "detail": detail, "remedy": remedy})

    is_vector = profile.get("kind") == "svg" and profile.get("shape_count", 0) > 0

    if not is_vector:
        for technique in ("line_draw_on", "multi_stroke_trace", "kinetic_typography",
                          "morph_shape", "geometric_construction"):
            block(technique, "NO_VECTOR_GEOMETRY",
                  "asset is raster or has zero drawable shapes; per-path timing is undefined",
                  "supply SVG, or vectorize and accept traced fidelity")

    if profile.get("geometry_fidelity") == "traced":
        for technique in ("line_draw_on", "multi_stroke_trace", "kinetic_typography"):
            block(technique, "TRACED_GEOMETRY",
                  "traced contours are always closed; trim-path cannot produce a stroke reveal",
                  "use mask_wipe or particle_dissolve")

    if profile.get("text_present") and not profile.get("text_outlined"):
        for technique in ("line_draw_on", "multi_stroke_trace", "kinetic_typography"):
            block(technique, "LIVE_TEXT",
                  f"{profile.get('text_count', 0)} live text node(s); renderer-dependent "
                  "glyphs break per-path timing",
                  "convert text to outlines before animating")

    fill_rules = profile.get("fill_rules") or {}
    if len(fill_rules) > 1 or fill_rules.get("evenodd", 0) > 0.5 * max(sum(fill_rules.values()), 1):
        for technique in ("line_draw_on", "multi_stroke_trace", "kinetic_typography", "morph_shape"):
            block(technique, "EVENODD_FILL_RULE",
                  "counters are parity-managed; re-winding subpaths breaks them",
                  "normalize to nonzero winding with opposite hole orientation")

    ink_ratio = profile.get("ink_ratio", 0.0)
    if profile.get("kind") == "raster" and not 0.01 < ink_ratio < 0.97:
        for technique in ("mask_wipe", "circular_sweep", "particle_dissolve"):
            block(technique, "DEGENERATE_SILHOUETTE",
                  f"ink_ratio={ink_ratio} outside (0.01, 0.97); no usable alpha mask",
                  "re-crop with padding")

    if profile.get("kind") == "raster":
        if (profile.get("component_count") or 0) < 2:
            block("separation_explode", "SINGLE_COMPONENT",
                  f"component_count={profile.get('component_count', 0)}; nothing to separate",
                  "use mask_wipe, circular_sweep, or orbit_rotate")
        if (profile.get("component_max_share") or 1.0) > 0.995:
            for technique in ("separation_explode", "separation_ordered", "particle_dissolve"):
                block(technique, "MONOLITHIC_MASS",
                      f"largest component holds {profile.get('component_max_share')} of ink",
                      "use mask_wipe or line_draw_on")

    if (profile.get("color_count") or 0) < 2 and (profile.get("gradient_count") or 0) == 0:
        block("gradient_sweep", "MONOCHROME",
              "single colour and no gradient; nothing to sweep",
              "use mask_wipe or geometric_construction")

    if profile.get("missing_targets"):
        for technique in TECHNIQUE_ROLES:
            block(technique, "BROKEN_USE_REF",
                  f"use references missing ids: {profile['missing_targets'][:3]}",
                  "fix ids in the source SVG")

    if (profile.get("filter_count") or profile.get("mask_count") or profile.get("clip_count")) and \
            profile.get("kind") == "svg":
        for technique in ("line_draw_on", "multi_stroke_trace", "kinetic_typography"):
            block(technique, "FILTERED_COMPOSITE",
                  "filter/mask/clip present; the visible silhouette is not the path geometry",
                  "flatten filters in the source, or accept mask work on the raster")

    if rung < 3 and profile.get("kind") == "svg":
        for technique in ("separation_explode", "separation_ordered", "kinetic_typography",
                          "geometric_construction", "scroll_scrub"):
            block(technique, "NO_INDEPENDENT_PARTS",
                  f"capability rung {rung}; the source exposes no independently "
                  "addressable parts",
                  "request a layered or outlined source")
    return gates


def _num(value, default=0.0) -> float:
    return float(value) if isinstance(value, (int, float)) else default


def evidence_rules(profile: dict) -> dict:
    """The rule table from references/technique-selection.md."""
    get = profile.get
    scores: dict[str, float] = {}
    fired: dict[str, list] = {}

    def fire(technique, rule, weight, reason):
        scores[technique] = scores.get(technique, 0.0) + weight
        fired.setdefault(technique, []).append(
            {"rule": rule, "weight": round(weight, 3), "reason": reason})

    open_ratio = _num(get("open_len_ratio"))
    stroke = bool(get("stroke_present"))
    stroke_norm = _num(get("stroke_width_norm"))
    caps = get("line_caps") or {}
    cap_total = sum(caps.values()) or 1
    holes = int(get("hole_count") or 0)
    nodes = int(get("nodes_total") or 0)
    components = int(get("component_count") or 0)
    disjoint = get("all_disjoint")
    entropy = _num(get("component_entropy"))
    max_share = _num(get("component_max_share"), 1.0)
    if get("part_max_share") is not None:
        max_share = _num(get("part_max_share"), 1.0)
    if get("part_entropy") is not None:
        entropy = _num(get("part_entropy"))
    sym_k = int(get("sym_rot_k") or 1)
    sym_rot = _num(get("sym_rot_score"))
    sym_mirror = _num(get("sym_mirror"))
    aspect = _num(get("aspect"), 1.0)
    aspect_signed = _num(get("aspect_signed"))
    complexity = _num(get("complexity"))
    colors = int(get("color_count") or 0)
    gradients = int(get("gradient_count") or 0)
    edge_density = _num(get("edge_density"))
    open_subpaths = int(get("open_subpath_count") or 0)
    translate_groups = int(get("translate_only_groups") or 0)
    centroid_offset = _num(get("centroid_offset"))
    solidity = _num(get("solidity"), 0.0)
    circularity = _num(get("circularity"))
    vertex_density = _num(get("vertex_density"))
    stroke_size = _num(get("stroke_size_ratio"))
    duplicates = int(get("duplicate_instance_count") or 0)
    clusters = max(int(get("duplicate_clusters") or 0), 1)

    if open_ratio > 0.40 and stroke:
        fire("line_draw_on", "R01", 0.45, f"open_len_ratio={open_ratio} with authored stroke")
    if open_subpaths >= 2 and open_ratio > 0.25:
        fire("line_draw_on", "R02", 0.20, f"{open_subpaths} open subpaths read as discrete strokes")
    if 0.015 <= stroke_norm <= 0.12:
        fire("line_draw_on", "R03", 0.15, f"stroke width {stroke_norm} is legible on screen")
    if caps.get("round", 0) >= 0.5 * cap_total:
        fire("line_draw_on", "R04", 0.10, "round caps dominate, which reads as drawn")
    if stroke and _num(get("stroke_width_cv")) < 0.25:
        fire("line_draw_on", "R05", 0.15, "near-constant stroke width, so constant-speed draw works")
    if get("corner_share") is not None and _num(get("corner_share")) < 0.20:
        fire("line_draw_on", "R06", 0.10, "smooth curvature suits a dash-offset reveal")
    if open_ratio < 0.05 and get("fill_present"):
        fire("line_draw_on", "R07", -0.30, "closed filled outline; a stroke reveal would crawl")
    if edge_density > 0.42:
        fire("line_draw_on", "R08", -0.20, f"edge density {edge_density} is too busy to trace")
    if nodes > 900:
        fire("line_draw_on", "R09", -0.15, f"{nodes} nodes make per-path dash timing impractical")

    if aspect > 3.0 and (holes >= 2 or components >= 3):
        fire("kinetic_typography", "R10", 0.50, f"wide mark with {max(holes, components)} letter-like parts")
    if aspect_signed > 0.55 and components >= 2:
        fire("kinetic_typography", "R11", 0.20, "landscape composition suits a horizontal lockup")
    if 3 <= components <= 14 and get("uniform_component_height"):
        fire("kinetic_typography", "R12", 0.20, "components share a cap height, so they read as letters")
    if holes >= 2 and aspect > 3.0:
        fire("kinetic_typography", "R13", 0.15, f"{holes} counters across a long bar read as letterforms")
    if 38 <= complexity <= 72:
        fire("kinetic_typography", "R14", 0.10, f"complexity {complexity} sits in the typographic band")
    if get("text_present") and not stroke and holes >= 2:
        fire("kinetic_typography", "R15", 0.20, "outlined text with counters and no stroke")

    if components >= 5 and disjoint:
        fire("separation_explode", "R16", 0.45, f"{components} disjoint components")
    if components >= 2 and disjoint and entropy > 0.7:
        fire("separation_explode", "R17", 0.25, f"many comparable parts, entropy {entropy}")
    if translate_groups >= 2:
        fire("separation_explode", "R18", 0.30, "source already offsets parts in translate-only groups")
    if int(get("named_part_count") or 0) >= 3:
        fire("separation_explode", "R18b", 0.25,
             f"the author named {get('named_part_count')} parts, so they are addressable")
        fire("separation_ordered", "R18b", 0.15,
             "named parts can be ordered by document order and overlap")
    if components >= 2 and max_share < 0.55:
        fire("separation_explode", "R19", 0.15,
             f"no dominant slab; the largest part holds {max_share} of the ink")
    if 0 < components < 3:
        fire("separation_explode", "R20", -0.35, f"only {components} component(s) to separate")
    if centroid_offset > 0.45:
        fire("separation_explode", "R21", 0.10, "asymmetric composition separates more legibly")
    if components >= 2 and max_share < 0.85:
        fire("separation_ordered", "R17", 0.20, "parts can be ordered by overlap and depth")

    if 0.01 < _num(get("ink_ratio"), 1.0) < 0.99 or get("kind") == "svg":
        fire("mask_wipe", "R22a", 0.15,
             "a whole-mark mask wipe is available on any drawable silhouette")
    if complexity >= 12:
        fire("mask_wipe", "R22", 0.20, f"complexity {complexity} supports a mask reveal")
        fire("mask_wipe_mark", "R22", 0.15, "a mark of this complexity suits a mask reveal")
    if _num(get("gradient_area_ratio")) > 0.05:
        fire("mask_wipe", "R23", 0.15, "gradient area needs a path-based mask")
    if max(sym_mirror, sym_rot) > 0.85:
        fire("mask_wipe", "R24", 0.10, "symmetry tolerates any wipe angle")
    if centroid_offset > 0.35:
        fire("mask_wipe", "R25", 0.10, "wipe from the light side of the composition")

    if sym_k >= 3 and sym_rot > 0.80:
        fire("circular_sweep", "R26", 0.40, f"{sym_k}-fold rotational symmetry makes a sweep native")
    if duplicates / clusters >= 4:
        fire("circular_sweep", "R27", 0.25, "repeating radial instances in the source")
    if 0.92 <= aspect <= 1.10 and circularity > 0.70:
        fire("circular_sweep", "R28", 0.25, "round badge shape")
    if sym_k < 2:
        fire("circular_sweep", "R29", -0.30, f"rotational order {sym_k} is not circular")

    if complexity >= 60:
        fire("particle_dissolve", "R30", 0.25, f"complexity {complexity} justifies the cost")
    if 4 <= colors <= 4096 and get("flat") is False:
        fire("particle_dissolve", "R31", 0.20, "multi-colour art dissolves attractively")
    if _num(get("hole_area_ratio")) > 0.20:
        fire("particle_dissolve", "R32", 0.15, "internal void reads as a particle field")
    if complexity < 38:
        fire("particle_dissolve", "R33", -0.35, f"complexity {complexity} does not justify a particle budget")
    if colors > 8192:
        fire("particle_dissolve", "R34", -0.20, "photographic source, not a logo")

    if solidity > 0.85 and vertex_density < 4:
        fire("geometric_construction", "R39", 0.20, "simple near-convex mark suits a construction reveal")
    if sym_k >= 4:
        fire("geometric_construction", "R38", 0.30, f"{sym_k}-fold symmetry builds from primitives")
    if 20 <= complexity <= 55 and solidity > 0.80:
        fire("extrusion_3d", "R46", 0.30, "convex mid-complexity mass extrudes cleanly")
    if stroke_size > 0.15:
        fire("extrusion_3d", "R47", 0.15, "slab-like mass suits depth stacking")
    if holes >= 3:
        fire("extrusion_3d", "R48", -0.20, f"{holes} counters self-occlude when extruded")

    if gradients >= 1:
        fire("gradient_sweep", "R42", 0.35, "the source authors a gradient")
    if _num(get("gradient_area_ratio")) > 0.15:
        fire("gradient_sweep", "R43", 0.25, "detected gradient area")
    if colors >= 3:
        fire("gradient_sweep", "R44", 0.15, f"{colors} quantized colors support a multi-stop sweep")
    if get("gradient_area_ratio") is not None and _num(get("gradient_area_ratio")) > 0.25:
        fire("gradient_sweep", "R45", 0.20, "soft shading present to sweep across")

    if complexity <= 55 and translate_groups >= 1:
        fire("bounce_elastic", "R49", 0.20, "simple positional mark reads well with a spring")
    if sym_mirror > 0.80:
        fire("bounce_elastic", "R50", 0.10, "symmetric bounce reads as intentional")

    if sym_k >= 2:
        fire("orbit_rotate", "R51", 0.35, f"rotational order {sym_k} is native to rotation")
    if 0.90 <= aspect <= 1.12:
        fire("orbit_rotate", "R52", 0.15, "near-square mark suits a controlled orbit")
    if _num(get("quadrant_entropy")) > 0.85:
        fire("orbit_rotate", "R53", 0.15, "balanced mass keeps rotation stable")
    if get("quadrant_entropy") is not None and _num(get("quadrant_entropy")) < 0.55:
        fire("orbit_rotate", "R54", -0.25, "unbalanced mass spinning reads as broken")

    if complexity <= 38 and max(sym_mirror, sym_rot) > 0.55:
        fire("idle_loop", "R55", 0.30, "simple and symmetric enough to loop")
    if get("dash_present"):
        fire("idle_loop", "R56", 0.20, "the source already authors a dash pattern")
    if complexity > 72:
        fire("idle_loop", "R57", -0.20, "a busy loop is visual noise")

    if aspect > 2.4:
        fire("scroll_scrub", "R58", 0.20, "wide lockups scrub well on scroll")
    if "wordmark" in (get("semantic_layer_hits") or []):
        fire("scroll_scrub", "R59", 0.25, "source names a wordmark layer, so independent timing is intended")

    if scores.get("line_draw_on", 0.0) >= 0.35 and open_subpaths >= 2:
        inherited = fired.get("line_draw_on", [])
        scores["multi_stroke_trace"] = scores["line_draw_on"] - 0.05
        carried = [dict(item, reason=item["reason"] + " (inherited from line_draw_on)")
                   for item in inherited]
        carried.append({"rule": "R02", "weight": -0.05,
                        "reason": f"{open_subpaths} discrete strokes need an explicit draw order"})
        if open_subpaths >= 3:
            scores["multi_stroke_trace"] += 0.10
            carried.append({"rule": "R02b", "weight": 0.10,
                            "reason": "three or more strokes need junction ordering"})
        fired["multi_stroke_trace"] = carried
    if sym_k >= 3 and aspect_signed > 0.3:
        scores["orbit_rotate_badge"] = scores.get("orbit_rotate", 0.0) * 0.8
        fired.setdefault("orbit_rotate_badge", []).append(
            {"rule": "R51b", "weight": 0.0, "reason": "badge composition suits an orbit ring"})
    if aspect > 3.0 and components >= 2 and complexity >= 20:
        scores["mask_wipe"] = scores.get("mask_wipe", 0.0) + 0.15
        fired.setdefault("mask_wipe", []).append(
            {"rule": "R25b", "weight": 0.15, "reason": "wide lockup takes a directional mask best"})

    return {"scores": scores, "fired": fired}


# Rules whose evidence comes from symmetry detection. When symmetry is
# ambiguous only these lose weight; a rule that reads node counts or areas is
# unaffected.
SYMMETRY_DEPENDENT_RULES = {"R24", "R26", "R27", "R38", "R50", "R51", "R51b",
                            "R53", "R54", "R55"}


def _haircuts(profile: dict, scores: dict, fired: dict) -> list:
    notes = []
    if profile.get("sym_ambiguous"):
        for technique, entries in fired.items():
            dependent = sum(item["weight"] for item in entries
                            if item["rule"] in SYMMETRY_DEPENDENT_RULES)
            if dependent and technique in scores:
                scores[technique] = scores[technique] - 0.5 * dependent
        notes.append("symmetry ambiguous; symmetry-derived evidence halved")
    if profile.get("style_resolution") == "partial":
        for technique in scores:
            scores[technique] -= 0.10
        notes.append("style resolution partial; every score reduced by 0.10")
    if (profile.get("confidence") or 1.0) < CONFIDENCE_FLOOR:
        for technique in scores:
            scores[technique] -= 0.20
        notes.append("overall confidence below the floor; every score reduced by 0.20")
    if profile.get("geometry_fidelity") == "traced":
        for technique in scores:
            scores[technique] *= 0.5
        notes.append("traced geometry; every score halved because traced is not authored")
    return notes


def recommend(profile: dict, min_confidence: float) -> dict:
    gates = feasibility_gates(profile)
    rule_result = evidence_rules(profile)
    scores = rule_result["scores"]
    fired = rule_result["fired"]
    haircuts = _haircuts(profile, scores, fired)

    ranked = []
    for technique, score in sorted(scores.items(), key=lambda item: -item[1]):
        if technique in gates or score < MIN_TECHNIQUE_SCORE:
            continue
        ranked.append({
            "technique": technique,
            "scenario_id": SCENARIO_IDS.get(technique, technique),
            "role": TECHNIQUE_ROLES.get(technique, "reveal"),
            "score": round(score, 3),
            "reference": _reference_for(technique),
            "rules": fired.get(technique, []),
        })

    primary = next((item for item in ranked if item["role"] == "reveal"), None)
    notes = list(haircuts)
    if primary is None:
        blocked_reveals = sorted(
            {gate["code"] for technique, entries in gates.items()
             if TECHNIQUE_ROLES.get(technique) == "reveal" for gate in entries})
        primary = {
            "technique": "mask_wipe",
            "scenario_id": SCENARIO_IDS["mask_wipe"],
            "role": "reveal",
            "score": 0.0,
            "reference": _reference_for("mask_wipe"),
            "rules": [{"rule": "FALLBACK", "weight": 0.0,
                       "reason": "every specialised reveal was gated; a whole-mark mask "
                                 "wipe is the only unblocked reveal"}],
        }
        notes.append(f"fallback to whole-mark mask wipe; gated reveal codes: "
                     f"{', '.join(blocked_reveals) or 'none available'}")
        ranked.insert(0, primary)

    reveal_count = sum(1 for item in ranked if item["role"] == "reveal")
    if reveal_count > 1:
        notes.append(f"{reveal_count} reveal techniques scored; kept the highest as primary "
                     "and demoted the rest")
    ranked = [item for item in ranked if item is not primary and item["role"] != "reveal"]

    supporting = [item for item in ranked
                  if item["role"] in {"transform", "surface", "loop"}
                  and item["score"] >= MIN_SUPPORT_SCORE][:2]
    if len(ranked) > len(supporting):
        notes.append("supporting gestures capped at two, and only above the support score floor")

    confidence = "provisional" if profile.get("kind", "").startswith("raster") else "inferred"
    if profile.get("kind") == "raster-unavailable":
        confidence = "blocked"

    blocked = []
    for technique, entries in sorted(gates.items()):
        for entry in entries:
            blocked.append({"technique": technique,
                            "scenario_id": SCENARIO_IDS.get(technique, technique),
                            "code": entry["code"],
                            "detail": entry["detail"],
                            "remedy": entry.get("remedy"),
                            "confidence": "blocked"})

    return {
        "primary": primary,
        "supporting": supporting,
        "blocked": blocked,
        "notes": notes,
        "min_confidence": min_confidence,
        "confidence": confidence,
    }


def split_after_taste(decision: dict, taste: dict) -> tuple:
    """Re-pick the primary and supporting gestures after the register veto."""
    if not taste.get("vetoed"):
        return decision["primary"], decision["supporting"]
    primary = decision["primary"]
    if primary and primary["technique"] in {entry["technique"] for entry in taste["vetoed"]}:
        survivors = [item for item in decision["supporting"]
                     if item["technique"] not in {e["technique"] for e in taste["vetoed"]}]
        fallback = {
            "technique": "mask_wipe",
            "scenario_id": SCENARIO_IDS["mask_wipe"],
            "role": "reveal",
            "score": 0.0,
            "reference": _reference_for("mask_wipe"),
            "rules": [{"rule": "TASTE_FALLBACK", "weight": 0.0,
                       "reason": "the recommended primary is vetoed by the register; a "
                                 "whole-mark mask wipe is the documented floor"}],
        }
        primary = survivors[0] if survivors else fallback
    return primary, decision["supporting"]


def _reference_for(technique: str) -> str:
    """Root-relative reference path, matching the house path convention."""
    mapping = {
        "line_draw_on": "references/patterns/line-drawing-and-trace.md",
        "multi_stroke_trace": "references/patterns/line-drawing-and-trace.md",
        "kinetic_typography": "references/patterns/kinetic-typography.md",
        "mask_wipe": "references/patterns/wordmark-and-lockup.md",
        "mask_wipe_mark": "references/patterns/geometric-constructive.md",
        "circular_sweep": "references/patterns/badge-and-emblem.md",
        "particle_dissolve": "references/patterns/matter-and-particles.md",
        "morph_shape": "references/patterns/geometric-constructive.md",
        "separation_explode": "references/patterns/separation-and-explode.md",
        "separation_ordered": "references/patterns/separation-and-explode.md",
        "geometric_construction": "references/patterns/geometric-constructive.md",
        "extrusion_3d": "references/patterns/separation-and-explode.md",
        "bounce_elastic": "references/contexts/playful-and-character.md",
        "orbit_rotate": "references/patterns/idle-and-ambient.md",
        "orbit_rotate_badge": "references/patterns/badge-and-emblem.md",
        "gradient_sweep": "references/contexts/premium-and-minimal.md",
        "idle_loop": "references/patterns/idle-and-ambient.md",
        "scroll_scrub": "references/patterns/idle-and-ambient.md",
    }
    return mapping.get(technique, "references/taxonomy.md")


# --------------------------------------------------------------------------
# Taste layer. Structure says what is possible; taste says what fits.
# A register veto is not a penalty. It is the brand declining the technique.
# --------------------------------------------------------------------------

# Registers mirror references/taste/brand-register.md. Keep the two in sync.
REGISTERS = {
    "premium": {
        "label": "premium and minimal",
        "max_overshoot": 0.0,
        "max_duration_s": 1.2,
        "max_gestures": 1,
        "veto": ["particle_dissolve", "bounce_elastic", "orbit_rotate", "idle_loop",
                 "geometric_construction", "separation_explode"],
        "prefer": ["line_draw_on", "mask_wipe", "gradient_sweep", "morph_shape"],
        "rationale": "the claim is that everything unnecessary was removed; a second "
                     "gesture or an effect contradicts it",
    },
    "heritage": {
        "label": "heritage and craft",
        "max_overshoot": 0.0,
        "max_duration_s": 3.0,
        "max_gestures": 1,
        "veto": ["particle_dissolve", "orbit_rotate", "geometric_construction",
                 "idle_loop", "bounce_elastic"],
        "prefer": ["line_draw_on", "multi_stroke_trace", "kinetic_typography",
                   "circular_sweep"],
        "rationale": "motion here is citation, not effect; any digital artefact reads "
                     "as a software startup claiming a history it does not have",
    },
    "technology": {
        "label": "technology and engineering",
        "max_overshoot": 0.02,
        "max_duration_s": 1.0,
        "max_gestures": 2,
        "veto": ["particle_dissolve", "bounce_elastic"],
        "prefer": ["geometric_construction", "separation_ordered", "line_draw_on",
                   "orbit_rotate"],
        "rationale": "the register wants a system reporting state, not a character "
                     "performing; organic easing lands in the mushy middle between "
                     "registers where nothing is claimed",
    },
    "playful": {
        "label": "playful and character",
        "max_overshoot": 0.15,
        "max_duration_s": 2.0,
        "max_gestures": 3,
        "veto": ["gradient_sweep"],
        "prefer": ["bounce_elastic", "kinetic_typography", "morph_shape"],
        "rationale": "the only register where elastic, secondary action, and "
                     "anticipation are licensed at full strength",
    },
    "wellness": {
        "label": "wellness and organic",
        "max_overshoot": 0.05,
        "max_duration_s": 3.0,
        "max_gestures": 1,
        "veto": ["particle_dissolve", "geometric_construction", "circular_sweep"],
        "prefer": ["idle_loop", "morph_shape", "mask_wipe"],
        "rationale": "cuts are percussive and this register has no percussion; a "
                     "visible loop seam undoes the calm it is claiming",
    },
    "corporate": {
        "label": "corporate and institutional",
        "max_overshoot": 0.0,
        "max_duration_s": 1.0,
        "max_gestures": 1,
        "veto": ["particle_dissolve", "bounce_elastic", "orbit_rotate",
                 "geometric_construction", "gradient_sweep", "idle_loop",
                 "morph_shape", "extrusion_3d"],
        "prefer": ["mask_wipe", "kinetic_typography", "line_draw_on"],
        "rationale": "the job is orientation, not expression; a fade is nearly always "
                     "the answer and any effect is a competence signal",
    },
    "sport": {
        "label": "energetic and sport",
        "max_overshoot": 0.03,
        "max_duration_s": 0.8,
        "max_gestures": 1,
        "veto": ["idle_loop", "morph_shape"],
        "prefer": ["separation_explode", "kinetic_typography", "circular_sweep"],
        "rationale": "the medium is fast; a slow logo stinger reads as a brand that "
                     "does not watch the sport",
    },
    "luxury": {
        "label": "bold and luxury",
        "max_overshoot": 0.0,
        "max_duration_s": 1.5,
        "max_gestures": 1,
        "veto": ["particle_dissolve", "bounce_elastic", "idle_loop",
                 "geometric_construction", "separation_explode", "kinetic_typography"],
        "prefer": ["mask_wipe", "gradient_sweep", "line_draw_on"],
        "rationale": "the rule is amplitude not duration: one very large very slow "
                     "move; a second move is the brand explaining itself",
    },
    "friendly": {
        "label": "friendly and family",
        "max_overshoot": 0.10,
        "max_duration_s": 2.0,
        "max_gestures": 2,
        "veto": ["gradient_sweep", "circular_sweep"],
        "prefer": ["bounce_elastic", "kinetic_typography", "idle_loop"],
        "rationale": "what distinguishes it from technology is low mass, real "
                     "overshoot, generous holds, and a slightly irregular rhythm; "
                     "mechanical evenness reads as institutional",
    },
    "precision": {
        "label": "technical and precision",
        "max_overshoot": 0.0,
        "max_duration_s": 0.6,
        "max_gestures": 1,
        "veto": ["bounce_elastic", "particle_dissolve", "idle_loop", "morph_shape",
                 "extrusion_3d"],
        "prefer": ["geometric_construction", "separation_ordered", "circular_sweep"],
        "rationale": "cornered, stepped, near-instant; the correct answer is often a "
                     "hard cut or motion blur rather than easing",
    },
    "editorial": {
        "label": "editorial and cultural",
        "max_overshoot": 0.03,
        "max_duration_s": 2.5,
        "max_gestures": 3,
        "veto": ["particle_dissolve", "orbit_rotate", "extrusion_3d"],
        "prefer": ["kinetic_typography", "line_draw_on", "mask_wipe"],
        "rationale": "type-led; the mark is usually the least important thing on "
                     "screen, so the system belongs to the type and the grid",
    },
}

# Expected views by one person. The frequency multiplier is the primary
# restraint mechanism: the same mark seen twice a day and once a year justify
# two completely different amounts of motion.
FREQUENCIES = {
    "rare": {"label": "about once a year", "duration_factor": 1.0,
             "gesture_factor": 1.0, "overshoot_factor": 1.0},
    "occasional": {"label": "about once a session", "duration_factor": 0.8,
                   "gesture_factor": 1.0, "overshoot_factor": 1.0},
    "daily": {"label": "about once a day", "duration_factor": 0.5,
              "gesture_factor": 1.0, "overshoot_factor": 0.0},
    "frequent": {"label": "dozens of times a day", "duration_factor": 0.25,
                 "gesture_factor": 1.0, "overshoot_factor": 0.0},
    "keyboard": {"label": "keyboard-initiated", "duration_factor": 0.0,
                 "gesture_factor": 0.0, "overshoot_factor": 0.0},
}

# The cliche register. A move is not dead because it is old; it is dead when it
# is available as a template and carries no brand-specific information.
CLICHES = {
    "particle_dissolve": ("free with every particle system; reads as scale without a "
                          "scale story", "B2B, financial, medical, legal, premium, and any "
                          "vertical feed", "a build from parts in assembly order"),
    "bounce_elastic": ("the default of every kinetic preset", "a playful or character "
                       "register, and only on an asset seen rarely", "an arrival with a "
                       "settle and no overshoot"),
    "orbit_rotate": ("implies an objecthood a flat mark does not have", "flat identities, "
                     "financial services, publishing, institutions", "a rotation inside "
                     "the plane that reveals a second reading"),
    "geometric_construction": ("one checkbox in a template", "marks with a published grid "
                               "or genuine primitive construction", "a build in the real "
                               "assembly order"),
    "gradient_sweep": ("the specular highlight is the cheapest way to imply premium, and "
                       "it has swept every logo", "a brand literally about reflective "
                       "material", "a reveal that follows the mark's own construction"),
    "separation_explode": ("reads as a complex system cheaply", "a system diagram or a "
                           "product family with a genuine hierarchy", "assembly in the "
                           "order the mark is constructed"),
    "kinetic_typography": ("per-letter spring is the default preset", "a word of six "
                           "characters or fewer in a playful voice", "type arriving on a "
                           "shared baseline in reading order"),
    "line_draw_on": ("trim path is one checkbox", "a signature, a hand-lettered wordmark, "
                     "an engraved mark, a single-stroke monogram", "an aperture or mask "
                     "reveal when the mark is not line art"),
    "mask_wipe": ("a wipe always works, so it is always used", "wordmarks with a strong "
                  "dominant axis", "a wipe whose axis derives from the mark's geometry"),
    "scroll_scrub": ("free with a page transition", "a genuine spatial narrative", "a "
                     "timed reveal that does not depend on the reader's scroll speed"),
    "idle_loop": ("ambient motion is added to fill an empty requirement", "a mark with a "
                  "documented reason to breathe, in a rare or occasional context", "a "
                  "static rest state"),
    "morph_shape": ("shape interpolation is one preset", "a mark that already changes "
                    "state in the product, such as an app icon and a logo", "a cross-fade "
                    "between two states with no shared geometry"),
    "circular_sweep": ("clock and iris wipes are the oldest moves in the book", "a mark "
                       "with genuine rotational symmetry", "a directional mask aligned to "
                       "the mark's dominant axis"),
    "extrusion_3d": ("pushed hard by render plugins; signals a 3D licence", "a brand for "
                     "which the object is genuinely solid", "flat construction with real "
                     "depth cues"),
    "multi_stroke_trace": ("draw-on applied to marks that are not line art", "marks with "
                           "genuine open strokes", "an aperture reveal"),
}


def taste_gate(profile: dict, ranked: list, register: str, frequency: str) -> dict:
    """Apply the register veto, the frequency budget, and the cliche check.

    A vetoed technique is removed from the ranking and reported with its reason.
    A cliche is reported as a warning, not a veto: a cliche used once, in the
    right register, with a stated referent is defensible.
    """
    result = {
        "register": register,
        "register_label": REGISTERS[register]["label"] if register in REGISTERS else None,
        "frequency": frequency,
        "frequency_label": FREQUENCIES[frequency]["label"] if frequency in FREQUENCIES else None,
        "budget": {},
        "permitted": [],
        "vetoed": [],
        "cliches": [],
        "notes": [],
    }
    if register not in REGISTERS or frequency not in FREQUENCIES:
        result["notes"].append("register or frequency not supplied; no taste gate applied")
        result["permitted"] = [item["technique"] for item in ranked]
        return result

    spec = REGISTERS[register]
    freq = FREQUENCIES[frequency]
    duration_ceiling = round(spec["max_duration_s"] * freq["duration_factor"], 3)
    gesture_ceiling = spec["max_gestures"] if freq["gesture_factor"] > 0 else 0
    overshoot_ceiling = round(spec["max_overshoot"] * freq["overshoot_factor"], 3)
    result["budget"] = {
        "duration_ceiling_s": duration_ceiling,
        "gesture_ceiling": gesture_ceiling,
        "overshoot_ceiling": overshoot_ceiling,
    }
    if frequency == "keyboard":
        result["notes"].append("a keyboard-initiated action should generally not animate; "
                               "the gesture ceiling is zero by policy")
    if overshoot_ceiling == 0.0 and spec["max_overshoot"] > 0:
        result["notes"].append("frequency suppresses overshoot to zero regardless of register")

    for item in ranked:
        technique = item["technique"]
        if technique in spec["veto"]:
            result["vetoed"].append({
                "technique": technique,
                "scenario_id": item["scenario_id"],
                "score": item["score"],
                "reason": spec["rationale"],
                "register": register,
            })
        else:
            result["permitted"].append(technique)

    for technique in result["permitted"]:
        if technique in CLICHES:
            why, dead_in, instead = CLICHES[technique]
            result["cliches"].append({
                "technique": technique,
                "why": why,
                "dead_in": dead_in,
                "replacement": instead,
                "verdict": "acceptable only with a stated brand referent and in a "
                           "register that licenses it",
            })

    preferred = [t for t in result["permitted"] if t in spec["prefer"]]
    if not preferred:
        result["notes"].append(
            f"no permitted technique sits in the {register} preferred vocabulary; the "
            "register's preferred set needs a source capability the profile does not report")
    else:
        result["notes"].append(f"register-preferred and permitted: {', '.join(preferred)}")
    if result["vetoed"]:
        result["notes"].append("a vetoed technique must be dropped from the ranking, not "
                               "demoted; record the register as the reason in the brief")
    return result


def apply_taste(ranked: list, taste: dict) -> list:
    """Remove vetoed techniques and promote a register-preferred survivor."""
    if not taste.get("vetoed"):
        return ranked
    vetoed = {entry["technique"] for entry in taste["vetoed"]}
    permitted = [item for item in ranked if item["technique"] not in vetoed]
    if permitted:
        return permitted
    # Every candidate was vetoed. A whole-mark mask wipe is the only move that is
    # never forbidden by a register, so it becomes the documented floor.
    fallback = {
        "technique": "mask_wipe",
        "scenario_id": SCENARIO_IDS["mask_wipe"],
        "role": "reveal",
        "score": 0.0,
        "reference": _reference_for("mask_wipe"),
        "rules": [{"rule": "TASTE_FALLBACK", "weight": 0.0,
                   "reason": "every recommended technique is vetoed by the register; a "
                             "whole-mark mask wipe is the only universally permitted reveal"}],
    }
    return [fallback]


# --------------------------------------------------------------------------
# Draw-on ordering
# --------------------------------------------------------------------------

def draw_plan(path: Path) -> dict:
    """Endpoint graph, Eulerian test, and per-subpath draw ranges."""
    tree = ET.parse(path)
    records: list[dict] = []
    for element in tree.getroot().iter():
        if _local(element.tag) != "path":
            continue
        data = element.get("d")
        if not data:
            continue
        for record in measure_subpaths(data):
            records.append(record)
    if not records:
        return {"available": False,
                "reason": "no path geometry found; a draw plan needs drawable paths"}

    points = [point for record in records for point in record["points"]]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    diagonal = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    tolerance = JUNCTION_TOLERANCE * diagonal

    def key(point):
        return (round(point[0] / tolerance), round(point[1] / tolerance))

    endpoints: dict[tuple, int] = {}
    for record in records:
        first, last = record["points"][0], record["points"][-1]
        for point in (first, last):
            endpoints[key(point)] = endpoints.get(key(point), 0) + 1
    odd = [vertex for vertex, degree in endpoints.items() if degree % 2 == 1]
    free = [vertex for vertex, degree in endpoints.items() if degree == 1]

    if len(odd) == 0:
        euler = "circuit: the mark can be drawn from any point without lifting the pen"
    elif len(odd) == 2:
        euler = "path: the mark can be drawn without lifting the pen, starting at one odd vertex"
    else:
        euler = (f"multiple: {len(odd)} odd vertices force at least "
                 f"{(len(odd) // 2) - 1} pen lifts")

    total = sum(record["length"] for record in records) or EPS
    cursor = 0.0
    order = sorted(records, key=lambda record: -record["length"])
    ranges = []
    for index, record in enumerate(order):
        share = record["length"] / total
        start_fraction = round(cursor, 4)
        cursor += share
        ranges.append({
            "index": index,
            "closed": record["author_closed"],
            "length": round(record["length"], 3),
            "share": round(share, 4),
            "start_pct": round(start_fraction * 100, 2),
            "end_pct": round(min(cursor, 1.0) * 100, 2),
            "duration_ms": round(max(share, EPS) * 1200, 1),
            "note": "duration is proportional to length so one pen reads at constant speed"
                    if len(records) > 1 else "single subpath, duration is the whole reveal",
        })

    return {
        "available": True,
        "subpath_count": len(records),
        "junction_tolerance": round(tolerance, 4),
        "free_endpoint_count": len(free),
        "odd_vertex_count": len(odd),
        "pen_lifts_required": max((len(odd) // 2) - 1, 0),
        "euler": euler,
        "start_point_rule": "prefer a free degree-one endpoint; then 12 o'clock clockwise for a "
                            "closed mark; then reading direction. Never start at a junction.",
        "symmetry_warning": "if the mark is mirror-symmetric and closed, do not start on the axis "
                            "of symmetry; it leaves a visible seam. Draw mirrored halves from "
                            "the apex instead.",
        "timing_model": "duration proportional to path length at a fixed pen speed; use a "
                        "designed sequence instead when the reveal should feel authored",
        "pen_lift_gap_ms": 250,
        "subpaths": ranges,
    }


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def profile(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".svg":
        result = profile_svg(path)
    elif suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff"}:
        result = profile_raster(path)
    else:
        raise RuntimeError(
            f"Unsupported source '{path.suffix}'. Supply an SVG or a raster image; "
            "the profiler does not read PDF, EPS, or AI sources.")
    rung, families = capability_rung(result)
    result["capability"] = {"rung": rung, "unlocks": families}
    warnings = result.get("warnings") or []
    result["warnings"] = warnings
    return result


def self_test(root: Path) -> int:
    """Dependency-free smoke test against the bundled fixtures."""
    failures = []
    fixture = root / "evals" / "files" / "layered-mark.svg"
    if not fixture.exists():
        print(f"FAIL: missing fixture {fixture}", file=sys.stderr)
        return 1
    result = profile(fixture)
    if result.get("shape_count", 0) < 1:
        failures.append("layered-mark.svg reported no drawable shapes")
    if result.get("subpath_count", 0) < 1:
        failures.append("layered-mark.svg reported no subpaths")
    if result.get("complexity", 0) <= 0:
        failures.append("complexity score was not computed")
    if result.get("ink_ratio", 0) <= 0:
        failures.append("ink ratio was not computed")
    plan = draw_plan(fixture)
    if not plan.get("available") or not plan.get("subpaths"):
        failures.append("draw plan produced no subpath ranges")
    decision = recommend(result, 0.0)
    if not decision.get("primary"):
        failures.append("no primary technique was recommended")
    if decision.get("confidence") == "observed":
        failures.append("a recommendation must never be reported as observed")
    gates = feasibility_gates(result)
    if not any("LIVE_TEXT" in entry["code"] for entries in gates.values() for entry in entries):
        failures.append("the live-text gate did not fire on a fixture that contains live text")

    if failures:
        print("FAIL: profiler self-test", file=sys.stderr)
        for message in failures:
            print(f"- {message}", file=sys.stderr)
        return 1
    print(f"note: profiled {fixture.name}: {result['shape_count']} shapes, "
          f"{result['subpath_count']} subpaths, complexity {result['complexity']} "
          f"({result['complexity_band']}), rung {result['capability']['rung']}")
    print(f"note: primary {decision['primary']['scenario_id']} at score "
          f"{decision['primary']['score']}, {len(decision['blocked'])} gated technique(s), "
          f"confidence {decision['confidence']}")
    print("\nPASS: profiler self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Profile a logo and rank the motion techniques its structure supports.")
    parser.add_argument("path", type=Path, nargs="?")
    parser.add_argument("--json", action="store_true", help="print only the JSON document")
    parser.add_argument("--draw-plan", action="store_true",
                        help="include the stroke draw-on ordering plan")
    parser.add_argument("--min-confidence", type=float, default=0.0,
                        help="minimum score for a technique to be reported (default 0.0)")
    parser.add_argument("--register", default="auto",
                        help="brand register for the taste gate: " + ", ".join(sorted(REGISTERS))
                             + ", or auto (default)")
    parser.add_argument("--frequency", default="occasional",
                        help="expected views by one person: " + ", ".join(sorted(FREQUENCIES))
                             + " (default occasional)")
    parser.add_argument("--self-test", action="store_true",
                        help="run the dependency-free smoke test and exit")
    args = parser.parse_args()

    if args.self_test:
        return self_test(Path(__file__).resolve().parent.parent)

    if not args.path:
        parser.error("a path is required unless --self-test is used")
    if not args.path.exists():
        print(f"Input does not exist: {args.path}", file=sys.stderr)
        return 2
    if not 0.0 <= args.min_confidence <= 1.0:
        print("min-confidence must be between 0 and 1.", file=sys.stderr)
        return 2
    if args.register != "auto" and args.register not in REGISTERS:
        print(f"register must be auto or one of {sorted(REGISTERS)}.", file=sys.stderr)
        return 2
    if args.frequency not in FREQUENCIES:
        print(f"frequency must be one of {sorted(FREQUENCIES)}.", file=sys.stderr)
        return 2

    try:
        result = profile(args.path)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    document = {
        "path": str(args.path),
        "source_kind": result.get("kind"),
        "profile": {key: value for key, value in result.items() if key != "capability"},
        "capability": result.get("capability"),
    }
    decision = recommend(result, args.min_confidence)
    ranked_all = [decision["primary"]] + decision["supporting"]
    taste = taste_gate(result, ranked_all, args.register, args.frequency)
    if args.register != "auto":
        decision["primary"], decision["supporting"] = split_after_taste(decision, taste)
        decision["taste"] = taste
    else:
        taste["notes"].append("register not supplied; the taste gate was not applied and "
                              "no register veto was enforced")
        decision["taste"] = taste
    if args.min_confidence > 0:
        decision["primary"] = decision["primary"] if \
            decision["primary"]["score"] >= args.min_confidence else None
        decision["supporting"] = [item for item in decision["supporting"]
                                  if item["score"] >= args.min_confidence]
    document["recommendation"] = decision
    if args.draw_plan and args.path.suffix.lower() == ".svg":
        try:
            document["draw_plan"] = draw_plan(args.path)
        except (ET.ParseError, OSError) as exc:
            document["draw_plan"] = {"available": False, "reason": str(exc)}
    document["disclaimer"] = (
        "Recommendations are inferred from measured structure, never observed. "
        "Connected components are diagnostic evidence, not guaranteed semantic logo layers.")
    print(json.dumps(document, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
