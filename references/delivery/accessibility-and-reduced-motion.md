# Accessibility and Reduced Motion

## Contents

- Baseline behavior
- Automatic motion
- Interaction motion
- Flashing and sound
- Assistive-technology semantics
- Deliverables

## Baseline behavior

Provide an approved static end frame whenever motion is not essential. The safest reduced-motion behavior is the final logo shown immediately, with an optional short opacity dissolve when continuity matters.

Do not preserve large scale, parallax, orbit, rotation, or translation merely because it is described as subtle.

## Automatic motion

For an automatic intro, provide a static poster/end frame and make the motion skippable or short where the runtime permits. The host must select the static/reduced asset when `prefers-reduced-motion` is active; CSS media queries do not automatically stop an MP4, GIF, or arbitrary Lottie player.

## Interaction motion

For hover, press, active, or selected states:

- Keep transitions around 90–180 ms unless a stronger expression is justified.
- Provide keyboard, pointer, touch, and focus parity.
- Never use motion as the only indicator of state.
- Keep a non-animated state available for reduced-motion users.

## Flashing and sound

Avoid rapid luminance changes and startling sound. If sound is added, make it optional and never use it to communicate essential information by itself. WCAG success criteria and recommendations have different conformance levels; document the target standard rather than calling every guideline a legal requirement.

## Assistive-technology semantics

Decorative logo marks may be `aria-hidden` when adjacent text already names the brand. Informative marks need an appropriate text alternative or accessible name. Do not make animation the only way to communicate a state or meaning.

## Deliverables

- Reduced-motion static or short dissolve
- Host-side selection logic for the reduced asset
- Keyboard/focus state where interactive
- Text alternative or poster frame
- No-motion preview for automatic intros
- Documentation of controls and stop/pause behavior
