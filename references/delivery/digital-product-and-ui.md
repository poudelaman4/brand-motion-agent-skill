# Digital Product and UI

Treat product motion as a frequency problem rather than a creativity problem: several platform rules forbid what a brand-motion deliverable would normally do, and the budget is set by how often the mark is seen.

## Contents

- The frequency rule
- Deliverables
- Where the platform forbids animation
- State machines and theming
- Budgets and formats
- Performance
- Failure modes
- QA

## The frequency rule

Judge motion by expected exposure. A mark seen twice a day and one seen once a year justify two different amounts of motion, and the high-frequency one normally gets less. Begin feedback within 0.1 s of the action, because a later change reads as lag. Keep productivity interface motion under 300 ms, and high-frequency interaction motion under 150 ms. Leave a keyboard-initiated action un-animated in most cases.

## Deliverables

| id | Deliverable | Duration or timing constraint | Size constraint | Delivery format | What makes it different |
|---|---|---|---|---|---|
| D-01 | App icon, default | Static | 1024×1024 px; 40×40 px legibility | PNG, no transparency | Stateless, scale-critical |
| D-02 | Icon appearance variants | Static | 1024×1024 px each | PNG each; `.icon` for layers | Six appearances per design |
| D-03 | Alternate or seasonal icon | Static | 6 assets per alternate | PNG set plus catalogue | Needs dark, clear, tinted |
| D-04 | Monochrome or themed icon | Static | Same mask and safe zone | PNG foreground plus mono | Silhouette is the deliverable |
| D-05 | Launch screen | Static by guideline | Matches orientation and appearance | `UILaunchScreen` or storyboard | Forbidden; see below |
| D-06 | Loading indicator | 1–2 s cycle, seamless | 24–48 px; ≤10 KB | Lottie or dotLottie | Runs indefinitely; seam must vanish |
| D-07 | Skeleton or shimmer loader | ~1.5 s shimmer; ~300 ms fade | Matches final box sizes | CSS gradient or Lottie | A structural promise |
| D-08 | Empty state | 700–1000 ms, ambient only | Unconstrained | Lottie, dotLottie, Rive, SVG | Only after a confirmed empty response |
| D-09 | Hover state | Feedback within 0.1 s; dwell 0.3–0.5 s | Unconstrained | CSS, WAAPI, Lottie | Often the first brand contact |
| D-10 | Press state | 50–100 ms; 150 ms reads as lag | Unconstrained | CSS `:active` or sprite | Pair with haptics |
| D-11 | Focus state | 0.1 s class; 240 ms ceiling | Unconstrained | CSS `:focus-visible` | Mark is usually decorative |
| D-12 | Navigation or view transition | 500 ms; 400 in, 200 out | Unconstrained | View Transitions API, CSS | Carries continuity |
| D-13 | Scroll-driven reveal | Bound to scroll distance | Unconstrained | `animation-timeline: scroll()` | User-paced; a flick misses it |
| D-14 | Page-load hero | LCP under 2.5 s [UNVERIFIED] | Under 300 KB [UNVERIFIED] | dotLottie; WebM VP9 | On the LCP path |
| D-15 | Notification and badge | Static; 40×40 px and 60×60 px | Notification sizes | Static PNG | Forbidden; system-owned |
| D-16 | Avatar and presence | Seamless loop; dot 10–12 px | Circular mask at 24 px | dotLottie | A status signal |
| D-17 | Cursor-reactive mark | 0.1 s class, 60 fps target | Unconstrained | WebGL, canvas, CSS | Main-thread-adjacent |
| D-18 | Persistent header mark | Continuous; 5 s pause rule | Unconstrained | dotLottie, CSS, SVG | Trips SC 2.2.2 most easily |
| D-19 | Onboarding sequence | 300–600 ms per step | Themes in one file | dotLottie with state machines | Stateful and branching |
| D-20 | Reduced-motion variant set | Fade replaces translation | Identical geometry | Static frame plus overrides | A required second deliverable |

## Where the platform forbids animation

Expect four refusals, each standing on a published guideline rather than on taste.

- **Launch screen.** Require it to be static, nearly identical to the first screen, textless, and unbranded unless the logo is part of that screen. Treat an animated splash as a violation, and place any splash at the start of onboarding. Expect no launch screen on macOS, visionOS, or watchOS, and a static one on tvOS.
- **Notification icon.** Ship a still, because the platform renders it at a fixed size and does not animate it.
- **Badge count.** Leave it to the system; badge animation sits outside brand control.
- **Reduce motion.** Replace translation with a fade, tighten springs, drop z-axis depth, and stop loops. Refuse a variant that only shortens durations.

## State machines and theming

Ship a stateful, themed, branching file when the asset must respond to theme, state, or a branch. Use the dotLottie format for that case: it bundles animations, images, themes, and state machines into one deflate archive, reported at 50–80% smaller than bare Lottie JSON and up to 10× smaller with embedded images. Weigh the bundle against the runtime: the player engine is about 500 KB compressed and sits on the critical path of the first frame, so preload it at route load. Weigh that against one file per theme, which multiplies assets by theme count and blocks runtime theme switching. Documented outcomes report 60–70% smaller files with most under 100 KB at 18.7 M impressions.

## Budgets and formats

| Surface | Ceiling |
|---|---:|
| Simple icon animation | ≤10 KB |
| UI animation | ≤50 KB |
| Complex vector animation | ≤150 KB |
| Page-load hero | ≤300 KB [UNVERIFIED] |
| Lottie JSON, raw | 1.2 MB gzips to about 120 KB |
| Player, `lottie` svg plus canvas plus html | about 77 KB min+gzip |
| Player, `lottie_light`, no `eval` | about 47 KB min+gzip |
| dotLottie engine | about 500 KB compressed |

Hold a delivery inside the ceiling for its own surface, not one global budget. Choose a container by what the browser decodes: WebM VP8 or VP9 alpha is the reliable transparent web choice, and MP4 alpha is not reliably decoded in browsers, so a transparent web asset needs a different container and should still carry an opaque fallback. Assume an effect that does not export at all is expressions, Glow, adjustment layers, particle-world, liquify, and turbulent-displace; blur, mask operations, and luma track-mattes vary by renderer. Prefer the light build where no `eval` is acceptable. Follow `alpha-and-codecs.md` for alpha semantics and `backgrounds-and-formats.md` for the composition matrix.

## Performance

Budget a frame rather than a whole animation: at a 60 fps target a frame leaves about 16.7 ms, and a permanently running vector player spends it on every frame of the session. Treat a persistent mark as the asset most likely to render continuously, and measure on the target device rather than assuming a desktop number holds on a mid-range phone. Write animation as a pure function of the frame or of a stable input wherever the surface is scrubbed, parallel-rendered, or re-created out of order, per `patterns/idle-and-ambient.md`. Expect scroll and cursor listeners to contend on one main thread, and measure with the real player loaded, because file size is not frame cost.

## Failure modes

**Animation on a launch screen**

**Symptom:** ship an animated splash, then meet a guideline violation and a slow perceived launch.

**Repair:** keep the launch screen static and move the brand moment to the start of onboarding.

**Loop with no pause control**

**Symptom:** run an endless header loop and fail SC 2.2.2, because auto-starting motion past 5 s in parallel with other content needs a mechanism.

**Repair:** ship a static default plus a pause control, or leave the mark static.

**Legible at full size, illegible in a notification**

**Symptom:** approve a mark at 1024 px, then see detail collapse at the 40×40 px notification size.

**Repair:** design and sign off at the smallest real render size first, then scale up.

**Shortened instead of replaced**

**Symptom:** add a `prefers-reduced-motion` rule that lowers duration while a script-driven player keeps running.

**Repair:** select a static or fade asset host-side, and ship the static frame for the reduced case.

## QA

- Render at the smallest real size for the surface, and confirm the mark reads there.
- Enable reduce motion and confirm translation is replaced rather than sped up, and that loops stop.
- Measure the delivered file against the surface ceiling, and record the figure.
- Check every persistent loop for a pause control against the 5 s threshold.
- Profile the real player on a mid-range device, and confirm LCP holds under 2.5 s.
- Re-render a scrubbed surface twice and compare frames for determinism.
- Record unsupported effects as `WARN` or `BLOCKED` rather than shipping a downgrade.

File-size ceilings and the 300 KB hero figure are community guidance, so treat them as `provisional` until a platform publishes its own limit.
