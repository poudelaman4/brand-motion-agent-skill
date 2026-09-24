# Research Sources

Retrieved or checked on 2026-09-25. Sources inform general principles only. Do not copy artwork, footage, code, or brand-specific expressions without checking rights.

## Skill authoring

- Agent Skills specification: https://agentskills.io/specification
- Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Skill evaluation: https://agentskills.io/skill-creation/evaluating-skills
- Description optimization: https://agentskills.io/skill-creation/optimizing-descriptions
- Anthropic skills examples: https://github.com/anthropics/skills
- Anthropic skill authoring guidance: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

## Motion and brand principles

- Motion Design School, logo animation principles: https://motiondesign.school/blog/animation-principles-in-logo-animation
- GitHub Brand Toolkit, motion principles: https://brand.github.com/motion/principles
- Thunder Lotus, lotus identity and animated logo: https://thunderlotusgames.com/blog/check-out-the-new-thunder-lotus-brand-identity
- Creative Bloq, motion in logo design: https://www.creativebloq.com/design/logos-icons/9-amazing-examples-of-motion-in-logo-design
- Material Design 3 motion and easing: https://m3.material.io/styles/motion/easing-and-duration
- Atlassian motion foundations: https://atlassian.design/foundations/motion

These are tutorials, brand precedents, or examples rather than normative logo standards.

## SVG, Lottie, and web animation

- SVG 2 specification: https://www.w3.org/TR/SVG2/
- SVG 2 processing/conformance modes: https://www.w3.org/TR/SVG2/conform.html
- MDN `pathLength`: https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/pathLength
- Compositing and Blending Level 1: https://www.w3.org/TR/compositing-1/
- Lottie shape specification: https://lottie.github.io/lottie-spec/1.0.1/specs/shapes
- dotLottie specification: https://dotlottie.io/spec/2.0/
- Lottie timeline versus state machines: https://docs.lottiefiles.com/en/integrations/figma/04_figma-to-lottie/timeline-vs-state-machines
- MDN web video codecs: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Video_codecs

Check the current specification version and target-player feature support before shipping SVG or Lottie assets.

## Accessibility and delivery

- WCAG 2.2 Pause, Stop, Hide: https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide
- WCAG 2.2 Animation from Interactions: https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
- WCAG 2.2 Three Flashes or Below Threshold: https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
- MDN reduced motion: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion
- Remotion transparent videos: https://www.remotion.dev/docs/transparent-videos
- Remotion playback transparency: https://www.remotion.dev/docs/videos/transparency
- Remotion performance: https://www.remotion.dev/docs/performance
- Remotion encoding: https://www.remotion.dev/docs/encoding
- FFprobe documentation: https://ffmpeg.org/ffprobe.html
- ORI VP8 encoding guidance: https://academysoftwarefoundation.github.io/EncodingGuidelines/EncodeVP8.html
- ORI VP9 encoding guidance: https://academysoftwarefoundation.github.io/EncodingGuidelines/EncodeVP9.html
- Apple ProRes support: https://support.apple.com/en-us/102207
- Apple ProRes white paper: https://www.apple.com/final-cut-pro/docs/Apple_ProRes.pdf

`prefers-reduced-motion` does not automatically control an MP4, GIF, or arbitrary Lottie player; the host must select a static or reduced asset.

## Source interpretation

- Official skill specifications define format and progressive disclosure; they do not prescribe a particular animation style.
- Brand pages are precedents, not universal rules. Extract principles such as restraint, narrative fit, and final-state clarity.
- Technical documentation is authoritative for renderer/codec behavior but may change; verify the installed version before relying on a flag or API.
- WCAG pages describe different conformance levels; do not label every recommendation as a universal legal requirement.
- Copyright and trademark rights remain with their owners. A reference does not grant permission to reuse its artwork, name, or footage.
