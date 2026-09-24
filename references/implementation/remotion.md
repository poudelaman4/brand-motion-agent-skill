# Remotion Implementation

## Contents

- Frame-driven architecture
- Local assets
- Tight crops
- Layer timing
- Renders
- Performance
- Transition-frame QA
- Example pattern

## Frame-driven architecture

Use `useCurrentFrame()` and `useVideoConfig()`. Keep all animation values deterministic functions of the frame. Avoid timers, state transitions, and CSS keyframes because Remotion renders frames independently and in parallel.

For a four-second 30 fps composition:

```ts
const { fps } = useVideoConfig();
const durationInFrames = 4 * fps;
```

The visible frame range is `0` through `durationInFrames - 1`. Layer intervals are half-open: `[startFrame, startFrame + durationFrames)`.

## Local assets

Use `staticFile()` with Remotion's `<Img>` or `<Video>` components. Keep assets in `public/` and use forward-slash relative paths. Do not depend on arbitrary absolute filesystem paths in the browser bundle.

## Tight crops

For high-resolution transparent layers, prefer a cropped PNG plus explicit source bounds over a full-canvas image per layer. A full-canvas 2508px RGBA image consumes substantial decoded memory when many layers are mounted. Position crops in a fixed square stage using normalized bounds and convert the pivot to a local transform origin.

## Layer timing

Define each layer as data:

```ts
type Layer = {
  id: string;
  bounds: [number, number, number, number];
  pivot: [number, number];
  startFrame: number;
  durationFrames: number;
  from: { x: number; y: number; scale: number; rotation: number; opacity: number };
  to: { x: number; y: number; scale: number; rotation: number; opacity: number };
  easing: string;
  zIndex: number;
  final_state: boolean;
};
```

Use clamped interpolation for a clean final state. If using `spring()`, tune and verify that it has settled before the hold.

## Renders

```bash
npx remotion render CompositionId output.mp4 --concurrency=2 --codec=h264 --crf=18
```

Use `--codec` and output options appropriate to the target. Validate with `ffprobe` and decode exact checkpoint/final frames. Keep square, vertical, alpha, white, and dark outputs as separate compositions driven by one canonical timing model.

## Transition-frame QA

For every opacity crossfade, render direct stills at the start, midpoint, and end, plus the frame immediately before and after the transition. Inspect the layer alone and in the complete composition at actual delivery scale. Then decode those same frame indices from the final encoded file. A direct still isolates composition-layer artifacts; a decoded frame checks codec, color, alpha, and player-delivery effects. A clean poster frame does not clear a transition.

## Performance

- Benchmark the lowest supported machine.
- Use concurrency appropriate to available RAM.
- Avoid per-frame segmentation or network image requests.
- Keep the number of simultaneously decoded transparent layers reasonable.
- Profile browser console errors and image decode warnings.
- Prefer tight crops when many high-resolution layers are mounted.

## Example pattern

For a detailed botanical mark with a sequential wordmark, begin the wordmark while the primary mark is still readable. Use a small frame stagger for letters, then guarantee a static canonical hold. This is a pattern, not a universal timing law; use the motion manifest and source-specific bounds.
