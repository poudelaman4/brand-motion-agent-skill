# Broadcast and Media

Treat a broadcast asset as a legal and engineering object rather than a creative deliverable: it is machine-inserted, frame-accurate, bound to published safe areas, and sometimes mandated by a regulator whose numbers cannot be negotiated.

## Contents

- What changes in broadcast
- Deliverables
- Safe areas
- Legal minimums
- Frame rate and delivery
- Constraints by deliverable
- Failure modes
- QA

## What changes in broadcast

Expect an asset to be inserted by playout rather than played by a viewer, so timing is frame-accurate. Require alpha normally, because the asset composites over live picture rather than a matte. Expect two frame-rate masters, 29.97i or 29.97d for NTSC and 25i for PAL. Treat a published broadcaster specification as versioned, and record every conflict with the brief as `blocked`.

## Deliverables

| id | Deliverable | Duration or cycle | Key safe-area rule | Delivery format | Differs from a logo reveal |
|---|---|---|---|---|---|
| B-01 | Station ident | 5–12 s | 90%×90% Safe Title | 422 HQ; 4444 alpha; MP4 | Cue-inserted; holds a static frame |
| B-02 | Corner bug | Hours; 6 s seamless loop | 90%×90% dual 4:3 and 16:9 | 4444 alpha; PNG sequence | Four corners, two lockups; tiny-scale legibility |
| B-03 | Sports score bug | Network bug on ≥90% of airtime | Team text in 90%×90% | Live data-driven template | Every frame a new string; reconfigures and returns |
| B-04 | Lower third | In 0.4–0.8 s, hold 4–8 s, out 0.3–0.6 s | 1728×972 px at 1080p | 4444 alpha; bound template | Text-bearing, so caption and translation rules attach |
| B-05 | Attribution lower third | As B-04, longer hold | 90%×90%; 4:3 protect variant | 4444 alpha; locked text box | Carries legal credit; separate element |
| B-06 | Programme open | 20 s–2 min | 90%×90%; 2.39:1 own conform | 4444 XQ matte; EXR | Cut to a hard first-scene frame |
| B-07 | End card | 5–15 s | 90%×90% | 4444 alpha mark plus 422 | Some territories demand a static frame |
| B-08 | Promo bumper | 5/10/15/20/30 s matrix | 90%×90% | 422 HQ; ProRes in MXF | Slot-locked; a tail error blacks the rotation |
| B-09 | Stinger | 0.5–2.0 s | Alpha mandatory | 4444, 16-bit lossless alpha | Bridges rather than announces |
| B-10 | Continuity | 2 min per period; 30 s hourly | 4:3 graticule for RP 218 | Exact-frame PNG; clock template | Clock-synchronised to signal |
| B-11 | Sponsor slate | ≥4 s | Letters ≥4% of height: ≥43.2 px cap at 1080p | 4444 alpha; locked type box | A compliance object; animation subordinate |
| B-12 | News strap | Seamless readable crawl loop | `origin (5% 5%)` / `extent (90% 90%)` | 4444 alpha; real-time template | Anchored to a scrolling crawl |
| B-13 | Cinema production logo | 3–7 s [UNVERIFIED] | 1.85:1 and 2.39:1 flat | DCP JPEG 2000 XYZ; no alpha | A distribution instrument in a fixed slot |
| B-14 | Awards title card | 2–8 s per nomination | 90%×90%; plus stage screen | 4444/XQ; live-render template | Live and one-take; glitches repeat |
| B-15 | Streaming-platform bug | ~5 s transient logo [UNVERIFIED] | 16:9 conformed to 4:3, 1080p, 2160p | IMF or DCP; mezzanine asset | Manifest-level and swappable |

## Safe areas

| Standard | Action safe | Title or graphics safe | Pixel box at 1080p |
|---|---:|---:|---:|
| SMPTE ST 2046-1:2009 | 93% W × 93% H of the production aperture | 90% W × 90% H | 1786×1004 px action; 1728×972 px title |
| SMPTE RP 218:2009 | 90% | 80% | Deprecated; CEA-708 captions only |
| SMPTE RP 2046-2:2009 | 90% × 90% only | 90% × 90% | Dual 4:3 and 16:9 authoring box |
| EBU R95 v1.1 (Jun 2017) | 3.5% per edge, 7% of image | 5% per edge, 10% of image | 576i/25 through 4320p |
| ATSC A/343:2018 §5.3 | `origin (5% 5%)` / `extent (90% 90%)` | IMSC1 prohibited outside it | Segment under 500 KB |
| ITU-R BT.1848-1 | 625 through 4320 line safe areas | Same set | Wide-screen 16:9 basis |

Keep significant elements inside the title-safe box and treat action safe as the crop bound. Compute the box before delivery: 1920 px × 90% is 1728 px and 1080 px × 90% is 972 px. Author a network bug to survive re-versioning to 4:3, because dual-safe authoring is the requirement when one market would otherwise need a re-crop.

## Legal minimums

| Requirement | Rule | Figure |
|---|---|---|
| Sponsorship ID, political advertising | Sized and timed to be read | ≥4% of picture height; ≥4 s |
| Foreign-government programming | Same sizing and duration, both ends | ≥4% of picture height; ≥4 s |
| Announcement placement | Beginning and conclusion | Once every 60 min at most |
| Sponsorship ID in one broadcast | One announcement normally suffices | 1 announcement |
| Station identification | Start and end of each period, and hourly | Hourly, as near the hour as feasible |
| Theatrical feature film | Sponsorship ID waived | Waived |

Read the sizing rule as cap height: 4% of 1080 px is 43.2 px. Treat a sponsor slate as a compliance object whose animation is subordinate to the legal minimum, and hold the mark readable for the full 4 s. Expect a sub-minimum design to be caught in quality control weeks later, so measure rendered cap height and record it.

## Frame rate and delivery

Produce two masters, 29.97i or 29.97d for NTSC and 25i for PAL, as separate files; re-timing rather than conforming shifts cue timing through drift. Budget the exchange by weight: ProRes 4444 runs at about 330 Mbps, or 146 GB per hour, and 4444 XQ at about 500 Mbps, or 223 GB per hour, at 1080p29.97, so a variant matrix is a storage decision. Keep 4444 alpha canonical per `alpha-and-codecs.md` and separate alpha, white, and dark compositions per `backgrounds-and-formats.md`. Declare premultiplication in the notes, because a mismatch darkens every soft edge. Resolve every asset to a static frame master control can hold.

## Constraints by deliverable

| id | In | Hold | Out or cycle | Extra obligation |
|---|---:|---:|---:|---|
| B-02 | within 6 s loop | 6 s | seamless | The 6 s loop period is the re-announce cadence |
| B-04 | 0.4–0.8 s | 4–8 s | 0.3–0.6 s | Six masters: 1, 2, 3 lines × with and without logo |
| B-05 | 0.4–0.8 s | 6–10 s | 0.3–0.6 s | Strict credit order; guild type minimums |
| B-08 | — | 5/10/15/20/30 s | — | Clean frame at exactly the slot |
| B-09 | — | 0.5–2.0 s | — | Seamless; no fade to black, no audio artefact |
| B-11 | — | ≥4 s | — | ≥43.2 px cap height at 1080p |

Drive a sports score bug from a named state matrix rather than a timeline.

| State | Configuration | Reconfiguration |
|---|---|---|
| Base | Network bug at rest | None |
| Score | Score module and clock on | Shrink or slide in footprint |
| Stat overlay | Bug reduced to make room | Hold the reduced state |
| Two bugs | Network bug plus local bug | Clear one; a fault |

## Failure modes

**Pillarboxed network bug**

**Symptom:** find a 16:9 bug letterboxed in a 4:3 pillarbox, with the loop period misaligned.

**Repair:** author to the 90%×90% dual-safe box and check the seam in the crop.

**Loop seam after hours of airtime**

**Symptom:** pass a seamless 6 s loop in review, then see a one-frame pop after hours of playout.

**Repair:** verify the last frame composites onto the first, and soak-test rather than review 30 s.

**Premultiplied alpha fringe**

**Symptom:** see a halo on every soft edge over live picture.

**Repair:** declare the alpha state, match the playout engine, inspect a decoded frame, per `alpha-and-codecs.md`.

**Lower third colliding with burned-in captions**

**Symptom:** place a name strap so low that open captions overlap it during a live hit.

**Repair:** raise the strap and hold graphic elements inside `origin (5% 5%)` / `extent (90% 90%)`.

## QA

- Check the composite over live picture, not a checkerboard, because alpha edges read differently against moving luminance.
- Overlay the SMPTE ST 2046-1 title box and the EBU R95 graphics-safe box on the 16:9 master, and clear both.
- Verify the 4:3 pillarbox crop separately, then check the 6 s loop seam frame by frame across the wrap.
- Inspect a decoded poster frame for premultiplication correctness and halo against a bright field.
- Check a compressed low-bitrate feed, and confirm thin type survives the codec rather than only the master.
- Measure rendered cap height and on-air duration for any sponsorship or political identification, and record every specification deviation as `WARN` or `BLOCKED`.

Conformance figures are read from published standards applied to a synthetic mark, so one network's tolerance stays `provisional` until measured on its master.
