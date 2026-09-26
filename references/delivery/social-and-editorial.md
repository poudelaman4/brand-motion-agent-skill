# Social and Editorial

Derive every frame from one canonical motion rather than re-authoring it per aspect ratio: platform overlays cover the outer margins, and a mark under an action rail or a caption block stays invisible however good the motion is.

## Contents

- Recompose, never crop
- Deliverables
- Platform covered zones
- Format reality
- The cinemagraph case
- Readability at thumbnail size
- Constraints
- Failure modes
- QA

## Recompose, never crop

Recompose, never crop. Read a horizontal lockup centre-cropped into a vertical frame as a reskin rather than a variant, because the crop keeps the original's empty margins and loses the mark's proportion.

Give each ratio its own composition, safe zones, and text zones from the canonical timing model, following `backgrounds-and-formats.md` for clear space. Hold the safe area as a parameter of each recomposition rather than a property of the master, and derive variants inside the source file, because hand-derived variants become forty slightly different logos.

```json
{
  "canonical_motion": "logo-reveal.v1",
  "derived_variants_only": true,
  "reverify_safe_zones_per_campaign": true,
  "recompositions": {
    "vertical_9x16": { "canvas": "1080x1920", "clear_top": "108px", "clear_bottom": "320px", "clear_right": "120px", "text_safe": "840x1280" },
    "stories_9x16": { "canvas": "1080x1920", "clear_top": "250px", "clear_bottom": "250px" }
  }
}
```

## Deliverables

| id | Deliverable | Canvas or duration constraint | Covered zones | Delivery format | What makes it different |
|---|---|---:|---|---|---|
| S-01 | Vertical cutdown | 1080×1920, up to 10 min | Right 120 px rail; bottom 320 px caption | MP4 H.264 | Recomposed, not cropped |
| S-02 | Square cutdown | 1080×1080 | Centre ~80% | MP4, GIF, Lottie | Read at 40 px in a grid |
| S-03 | Landscape cutdown | 1920×1080 | Title and CTA overlays | MP4, WebM, HLS | Broadcast layout, no regulatory weight |
| S-04 | Stories or Reels frame | 1080×1920 | Top and bottom 250 px | MP4, GIF | Progress bar; may show for 2 s |
| S-05 | Cinemagraph | 2–4 s loop | None | MP4 muted, GIF, Lottie | A still image with one pulse |
| S-06 | Looping GIF | 256 colours, 4–5 s | None | GIF | Only format reaching email and chat |
| S-07 | Animated sticker | 512×512 px source | Platform mask, segmentation | PNG sequence, Lottie, APNG | A character, not a mark |
| S-08 | Kinetic-type poster | 3–10 s; readable inside 1 s | Authored crop | MP4, WebM, template | Wordmark animates, mark punctuates |
| S-09 | Thumbnail, cover frame | 1920×1080 px; 3:4 and 4:5 feed | End-screen and cover-crop zones | JPG, PNG, WebP | Extracts the final frame |
| S-10 | Carousel frames | 1080×1350 px, 1080×1440 px | 50–120 px sides | Static, optional micro-animation | Mark appears once |
| S-11 | Live or looping badge | Legible at 10–16 px | N/A | Static vector; pulse only with a control | A false live state |

## Platform covered zones

Platform interface overlays move with every release, so these figures are the most volatile numbers in the package. Treat `verified_on` as a hard expiry: a row older than 90 days is `BLOCKED` for placement, not `provisional`. Re-verify per campaign from a current interface capture and prefer that capture over any carry-over from this table.

| Surface | Covered zone | Status | Verified on |
|---|---|---|---|
| TikTok vertical | Top 108 px, bottom 320 px, left 60 px, right 120 px; text-safe ~840×1280 px | `provisional`; ranges reported top 130–250 px, bottom 250–320 px | 2026-09-26 |
| Stories | Top and bottom 250 px; Highlights safe content 1080×1080 px, 420 px clear | `provisional` | 2026-09-26 |
| Reels, boosted | 1010×1280 px safe zone, 220 px from top, 420 px from bottom | `provisional` | 2026-09-26 |
| Reels cover crop | Key elements inside the centred 1080×1350 px zone | `provisional` | 2026-09-26 |
| Feed carousel | Side margins 50–120 px for platform icons | `provisional` | 2026-09-26 |

Keep essential content out of the outer 250–450 px of a 1080×1920 px frame, and treat a mark under the action rail as undelivered.

## Format reality

| Format | Colour count | Alpha | Alpha quality | File-size behaviour | Where it still works |
|---|---|---|---|---|---|
| MP4 H.264 | Full | None | N/A | Predictable; up to 287 MB | Universal video |
| WebM VP9 alpha | Full | Yes | Good, banding risk | Grows with duration | Modern web needing alpha |
| GIF | 256 colours | Binary | Crumbled on soft edges | 4–5 s reaches several MB | Email and chat, where nothing else runs |
| APNG | Full | Yes | Good | Heavier than GIF | Chat clients with support |
| Lottie, dotLottie | Vector | Yes | Resolution-independent | Rises with path count | Web, stickers, loops |
| Static PNG, WebP | Fixed | PNG only | Good | Flat | Thumbnails, fallbacks |

Expect GIF to carry binary transparency and a 256 colour count, so it crumbles exactly the soft edges a logo is made of, and accept it as the only format that plays in email and chat. Hold a looping GIF to WCAG 2.2.2 (A): stop it after a stated cycle count or offer a control, per `delivery/accessibility-and-reduced-motion.md`. Assume frame 1 is the deliverable for most of the audience, because Outlook desktop uses the Word HTML engine and shows the first frame only. Forbid borders or drop shadows on an embedded animated GIF, which converts it to a static JPG on send.

## The cinemagraph case

Define a cinemagraph as a still image with one small looping element, and reject a full logo reveal as the wrong artefact, because the stillness is the design. Hold the loop as the entire constraint: require every moving element to return to its first frame with identical velocity, normally over 2–4 s. Fail the asset when too much moves, since a cinemagraph animating the whole mark is a reveal with extra frames.

## Readability at thumbnail size

Treat the grid thumbnail as the real size a social logo is often seen at, and assume a mark designed full-frame then read at feed-thumbnail size has usually failed. Read a 1080×1080 px square cutdown at roughly 40 px, and a badge at 10–16 px. Author the thumbnail crop rather than accepting an automatic one, and extract the thumbnail as the asset's final frame.

## Constraints

| id | Duration | Safe content area | Ceiling | Playback |
|---|---|---|---:|---|
| S-01 | Up to 10 min | 840×1280 px | 287 MB | Once |
| S-02 | 3–15 s | Centre ~80% | 287 MB | Loop permitted |
| S-03 | 5–20 s | 90% title box | 287 MB | Once |
| S-04 | 2–15 s; may show for 2 s | 1080×1080 px | 287 MB | Once |
| S-05 | 2–4 s | Full frame | 287 MB | Seamless loop |
| S-06 | 4–5 s; three cycles then stop | Full frame | Several MB | Stop at 5 s or control |
| S-07 | 1–3 s | 512×512 px | 500 KB | Loop permitted |
| S-08 | 3–10 s; readable inside 1 s | Authored crop | 287 MB | Once |
| S-09 | Static | End-screen zones | 2 MB | N/A |
| S-10 | Static per frame | 50–120 px sides clear | 2 MB | N/A |
| S-11 | Persistent | N/A | 10 KB | Loop only with a control |

## Failure modes

**Pillarboxed vertical master**

**Symptom:** centre-crop a 16:9 master into 1080×1920 px, then read the bars as a bad export rather than a bad composition.

**Repair:** author a 9:16 recomposition and check the 840×1280 px text-safe box.

**Mark under the action rail**

**Symptom:** place the lockup full-frame on vertical, then find the right 120 px hidden behind like, comment, and share controls.

**Repair:** shift left of the rail and re-verify against the current interface.

**Payoff after frame one**

**Symptom:** build a reveal resolving at 0.8 s, then see a static mark in every Outlook desktop inbox.

**Repair:** design frame 1 as the finished mark and treat motion as enhancement.

**Cinemagraph with too much movement**

**Symptom:** animate the whole mark, then lose the still frame that made the format work.

**Repair:** freeze the mark and loop one element at matching velocity.

## QA

- Capture the platform's own interface overlay on the frame, not the bare canvas, and confirm the mark clears every action rail, caption block, and progress bar.
- Re-verify each safe zone against a current interface capture per campaign, and record it as `observed` or `provisional`.
- Composite the last frame onto the first and inspect the seam for a pop, a velocity change, or a duplicated frame.
- Read the mark at 40 px in a grid, at 10–16 px as a badge, and at full frame; reject any failing size.
- Confirm frame 1 carries the complete mark and the call to action, and that no essential copy exists only in motion.
- Decode the encoded file rather than the source composition, per `alpha-and-codecs.md`, and record dimensions, frame rate, and duration.

Treat the covered-zone figures above as `observed` on a single platform release and `inferred` beyond it, so hold every one `provisional` until re-measured in the campaign's own interface.
