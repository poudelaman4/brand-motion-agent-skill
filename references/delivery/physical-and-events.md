# Physical, Retail, and Events

Treat an off-screen brand asset as an installation rather than a file: it meets a viewer at a distance nobody chose, in light nobody art-directed, on hardware nobody specified, for eight hours a day, and it should survive the first frame after a power cut.

## Contents

- What changes off-screen
- Deliverables
- Aspect ratios and led walls
- The long loop
- Interactive and realtime
- Constraints
- Failure modes
- QA

## What changes off-screen

Count five variables a screen at 40 cm does not have. Expect a viewing distance set by furniture rather than composition, commonly 3–10 m for a walking viewer. Expect daylight through a shopfront, where black level becomes the binding problem. Expect a canvas fixed by a cabinet or a bezel. Expect an installed player that may be a decade old. Expect a loop measured in hours.

Hold the mark to one test before designing anything: watched at 3 m in a bright room by someone already walking past. That test normally eliminates multi-step builds, particles, depth, and any stroke under about 3 px at installation scale. Reduce to one gesture, then raise size and contrast until it survives the room. Design at the player's capability rather than at the review monitor, and follow `backgrounds-and-formats.md` for recomposition and `alpha-and-codecs.md` for the encode.

## Deliverables

| id | Deliverable | Binding constraint | Canvas or loop | Delivery format | What makes it different |
|---|---|---|---|---|---|
| R-01 | In-store signage loop | Walking viewer at 3–10 m for 3–8 s | 16:9 at 1920×1080; 1–2 min loop | MP4 H.264 Main, 4–12 Mbps, ≤ 10 MB, 24–30 fps | Judged on ambient light, not a calibrated display |
| R-02 | Portrait signage loop | A separate master is mandatory, never a crop | 9:16 at 1080×1920; 1–2 min loop | As R-01 | First impression; shot by passers-by |
| R-03 | Window display | Ambient-light contrast | Screen-native, often ultra-wide | MP4 H.264, high bitrate | Vanishes at midday on a crushed black |
| R-04 | Menu board videowall | Dynamic aspect: 16:9 per panel, 4:1 across the wall | Per-panel plus one stitched master | MP4 per panel; stitched master; live HTML5 | The only context where a bezel splits the mark |
| R-05 | Packaging with AR | Print 300 dpi CMYK plus a marker; two masters of one idea | Marker area reserved; framed for a portrait phone at 30–50 cm | PDF/AI vector; glTF/GLB or USDZ | Print is the weaker master: foil, shrink, curvature |
| R-06 | Event stage and LED wall | Pixel pitch sets the source resolution | Cabinet grid; 16:9, 32:9, or custom | MP4 at native resolution; screen plus IMAG feeds; cue sheet | Live, one-take, un-recoverable |
| R-07 | Wayfinding kiosk | Interruptible at any frame | Often 9:16; 10–15 s still dwell; attract loop | HTML5 or WebGL; MP4 for attract | A half-played reveal is the visible bug |
| R-08 | Environmental projection | Warping, not scaling; multi-surface | Per-surface, non-rectangular; 10–15 s stills | MP4 multi-channel; parallel DMX track | Straight edges become curves |
| R-09 | Merchandise | Minimum physical size, about 0.275 in emblem width | No canvas; stated in mm and inches | Vector EPS/SVG/PDF; raster at the vendor's dpi | No motion at all |
| I-01 | WebGL or canvas hero | 60 fps, 16.7 ms per frame | Responsive; degrades under reduced motion | Three.js or canvas plus glTF; dotLottie | Quality is a function of the device |
| I-02 | Augmented reality | 13.9 ms at 72 Hz, 11.1 ms at 90 Hz | 1:1 passthrough; anchored in world space | glTF/GLB, USDZ, WebXR | The mark is pinned to a moving body |
| I-03 | Immersive reality | Fragment-bound; 7–10 ms with impostors against up to 60 ms for mesh | Per-eye stereoscopic | glTF/USDZ, KTX2, Draco | The mark becomes architecture |
| I-04 | Game and app branding | 2–6 s; skippable after the first run | 16:9 and 21:9; console safe rect unpublished | In-engine sequence; pre-rendered ProRes; video texture | Boot-time and memory-constrained |
| I-05 | In-game brand surface | Mod-safe and data-bound; a material, not a video | Any user-supplied surface | glTF/FBX plus atlases; decals | Legible on a surface a user controls |
| I-06 | Kiosk and touch installation | Public, unsupervised, all day; recover from any interruption | Projection or multi-display; loop-seam critical | Real-time WebGL or Three.js; MP4 fallback | A broken state is a public incident |
| I-07 | Projection mapping | Authored in the projection's warped space | Per-surface, non-rectangular; blend overlaps | Pre-rendered MP4 or live render | Every straight edge bends |
| I-08 | Realtime broadcast graphics | Data arrives late, wrong, or missing | 16:9 inside the 90% × 90% title box | Templated graphics engine, not a file | The mark is a template variable |
| I-09 | Parameterised brand system | Every seed on brand and inside the safe area | Parameter space bounded, not the mean | dotLottie state machines; WebGL runtime | The deliverable is a rule set, not an asset |

## Aspect ratios and led walls

| Installation | Ratio | Native size | Tolerance |
|---|---|---|---|
| Signage LCD, landscape | 16:9 | 1920×1080 px | 1280×720 and 3840×2160 also accepted |
| Signage LCD, portrait | 9:16 | 1080×1920 px | 2160×3840 px for 4K |
| Videowall, four panels | 4:1 | One stitched master | Per-panel masters required as well |
| LED cabinet P1.25 | Cabinet grid | 960×540 px | 4 × 2 wall = 3840×1080 px |
| LED cabinet P1.45 | Cabinet grid | 825×464 px | — |
| LED cabinet P1.875 | Cabinet grid | 640×360 px | — |
| LED cabinet P2.5 | Cabinet grid | 480×270 px | — |
| Retail window | Screen-native | Often ultra-wide | Measure the fit-out |
| Projection surface | Non-rectangular | Per-surface | Geometry is the canvas |

Design to the grid rather than to 16:9. Treat the cabinet as the unit of composition, land structural elements on cabinet boundaries, and hold the standard splice area at or below 1920×1080 px.

Treat an LED wall as something other than a monitor. Expect viewing at distance, often at an angle from the floor, often in daylight or stage wash, and expect pixel pitch to decide which detail survives. Expect a closest comfortable viewing distance of about 2 × pitch and a comfortable distance near 3.4 × pitch. Expect refresh up to 3840 Hz against a 50 or 60 Hz frame rate, which is why camera behaviour differs from an LCD.

Preserve under recomposition: identity geometry, clear space, the anchor, stroke weight in millimetres rather than percentages, the full-visible hold, and the loop period. A recomposition that keeps the mark's share of frame but not its stroke weight has not preserved the mark.

Apply a provisional floor on a large display [UNVERIFIED]: minimum stroke at about 1/32 of rendered mark height, minimum cap height at about viewing distance ÷ 250, then verify in the room rather than trusting the ratio.

## The long loop

Treat eight hours of playback as a different discipline from a four-second reveal. A reveal is judged once by one viewer. A loop is judged thousands of times by viewers arriving at a random phase, most of whom should see one cycle and never learn that it repeats.

Build the long loop from a short verified cycle rather than from one long timeline. Assemble a playlist whose total length is an exact multiple of the cycle, and reject a master whose period does not divide the playlist evenly, because a partial cycle at the wrap reads as a seam within a day.
| Property | Requirement | Basis |
|---|---|---|
| Short cycle | 8–20 s, a whole number of frames | [UNVERIFIED] working range |
| Still dwell | 10–15 s | observed |
| Full content loop | 1–2 min in a shop window | observed, secondary |
| Seam | Frame N matches frame N+cycle in position, scale, rotation, colour, alpha, and velocity | `patterns/idle-and-ambient.md` |
| Drift | Zero cumulative offset across the playlist | inferred |
| Uptime | 8 h unattended | observed |

Expect drift from the player rather than the file: a CMS that re-times on ingest, a player that drops a frame and resumes at the wrong phase, a clock that does not divide the loop. Log the loop count against wall time after a full day.

Expect burn-in and colour shift from continuous playback. Expect static bright elements to imprint on LCD and OLED panels, LED modules to age unevenly so panel-to-panel colour diverges, and a bright wall to warm and shift over the first hour. Provide a moving or darkened frame in every cycle and set a brightness ceiling rather than leaving the installer to guess.

## Interactive and realtime

Treat input-driven work as a performance problem before a creative one. Hold 16.7 ms per frame at 60 fps, 13.9 ms at 72 Hz, and 11.1 ms at 90 Hz, and count the device pixel ratio as the usual multiplier on a 3× phone. Cap the pixel ratio, disable frame interpolation on a 30 fps source, and preload the engine, because an engine on the critical path of the first frame misses the budget before the animation starts.

Write every animated value as a pure function of the frame and of a stable input, per `patterns/idle-and-ambient.md`, so a re-created or out-of-order frame renders identically. Derive values from state rather than from elapsed time, or an interrupted session resumes mid-reveal.

Require degradation rather than a stall. Reduce the pixel ratio, drop shadows, fall back to a static frame, and suspend the loop off-screen. Never let a slow frame become a frozen one, and ship a static composition for reduced motion rather than a stalled first frame.

Owe a passer-by who cannot be taught. Assume no instruction gets read and no mode gets chosen. Begin feedback within 0.1 s, return to the attract loop from any interruption, and never leave a half-played frame on screen. Touch-target size, reach range, and contrast are accessibility requirements, and the reset path is a public-safety requirement.

## Constraints

| Deliverable | Loop period | Minimum on screen | Viewing distance | Play once or loop |
|---|---:|---:|---:|---|
| Signage loop | 1–2 min | 10–15 s still; 3–8 s motion | 3–10 m | Loop; no control on site |
| Window display | 1–2 min | 10–15 s | 2–15 m | Loop |
| LED wall | Cue-driven | ≥4 s for a compliance lockup | 3.4 × pitch to the rear rows | Once, per cue |
| Kiosk attract | 8–20 s | 10–15 s | 0.4–0.7 m | Loop, with timeout |
| Environmental projection | Minutes | 10–15 s for stills | 5–50 m | Loop |
| Touch installation | 8–20 s | Until idle, up to 60 s | 0.4–1.5 m | Loop with reset |
| Realtime graphics | Continuous | ≥4 s; letters ≥4% of height | Broadcast viewing | Continuous |
| Game ident | 2–6 s | One per boot | 0.5–3 m | Once, skippable after the first run |
| Merchandise | None | Static | As printed | Never |

## Failure modes

**A loop seam found after installation**

**Symptom:** pass review in a dark room, then see a hitch, a colour step, or a partial cycle at the wrap in a bright shopfront on day two.

**Repair:** rebuild from a short whole-frame cycle whose length divides the playlist, re-check the seam at 3 m, and log the loop count against wall time after 24 h.

**Legible on the proof, illegible in the room**

**Symptom:** approve a fine-stroke mark on a calibrated 24 in monitor, then watch the strokes close up at 3–10 m.

**Repair:** hold the minimum stroke at about 1/32 of rendered mark height [UNVERIFIED], enlarge until the full-visible hold survives the real distance, and sign off in the room.

**A projection that only works from one angle**

**Symptom:** approve a mapping from the calibration position, then see keystoning and a bent mark from every seat but that one.

**Repair:** author in the projection's warped space, verify from the extremes of the audience area rather than the centre, and accept a mark that survives the worst angle.

**An upscaled master on a fine-pitch wall**

**Symptom:** design 1920×1080 and upsample to a P1.25 wall at 3840×1080, then see a soft, shimmering mark on a 700 nit surface.

**Repair:** render at the cabinet grid, hold the splice area at or below 1920×1080 px, and check contrast against stage wash rather than a bright room.

**A kiosk that never returns to rest**

**Symptom:** interrupt the piece, or leave it running 8 h, and find a half-played frame, a lost pointer capture, or a frame rate decaying as memory grows.

**Repair:** re-enter the attract loop from any frame, derive values from the frame number rather than elapsed time, and re-create the scene to cap long-session memory.

## QA

- View the mark from the real distance in ambient light, at 3 m for a 16:9 signage screen and 3.4 × pitch for an LED wall, and confirm stroke and counter shapes hold.
- Play the delivered loop continuously for at least 8 h, then check the seam, the loop count against wall time, black level in full daylight, and panel-to-panel colour divergence.
- Render each LED cabinet-native master and confirm no upscaling occurs on the wall.
- Recreate a frame out of order and confirm it renders identically, per `patterns/idle-and-ambient.md`.
- Interrupt a kiosk at ten random frames and confirm each returns to a clean attract frame within one cycle.
- Measure frame time on the installed player, not the authoring machine, and confirm reduced motion yields a static composition per `accessibility-and-reduced-motion.md`.

Loop-period ranges, cabinet tolerances, and the large-display type floors are inferred from vendor practice rather than a published standard, so treat them as `provisional` until measured on the installed hardware.
