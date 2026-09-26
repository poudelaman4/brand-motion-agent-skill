# Research Sources

Retrieved or checked on 2026-09-26. Sources inform general principles only. Do not copy artwork, footage, code, or brand-specific expressions without checking rights.

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
- SVG 2 specification painting chapter: https://www.w3.org/TR/SVG2/painting.html
- SVG 2 specification paths chapter: https://www.w3.org/TR/SVG2/paths.html
- MDN `stroke-dasharray`: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray
- MDN `stroke-dashoffset`: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dashoffset
- MDN `stroke-linecap`: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-linecap
- MDN `pathLength` attribute reference: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/pathLength
- MDN `SVGGeometryElement.getTotalLength()`: https://developer.mozilla.org/en-US/docs/Web/API/SVGGeometryElement/getTotalLength
- MDN `SVGTextContentElement` per-glyph measurement: https://developer.mozilla.org/en-US/docs/Web/API/SVGTextContentElement
- MDN `textPath`: https://developer.mozilla.org/en-US/docs/Web/SVG/Element/textPath
- MDN `font-variation-settings`: https://developer.mozilla.org/en-US/docs/Web/CSS/font-variation-settings
- Lottie shape layer specification: https://lottiefiles.github.io/lottie-spec/specs/shapes
- Lottie constants specification: https://lottiefiles.github.io/lottie-spec/specs/constants/
- dotLottie specification v1: https://dotlottie.io/spec/1.0
- WebKit bug 72401, `pathLength` support: https://webkit.org/bugzilla/show_bug.cgi?id=72401

Check the current specification version and target-player feature support before shipping SVG or Lottie assets.

## Renderers and implementation

- Remotion interpolate: https://www.remotion.dev/docs/interpolate
- Remotion spring: https://www.remotion.dev/docs/spring
- Remotion transparent videos: https://www.remotion.dev/docs/transparent-videos
- Remotion encoding: https://www.remotion.dev/docs/encoding
- GSAP DrawSVGPlugin: https://gsap.com/docs/v3/Plugins/DrawSVGPlugin/
- Motion issue 3301, Safari zoom and dash normalization: https://github.com/motiondivision/motion/issues/3301
- jsdom issue 1330, `getTotalLength` undefined without layout: https://github.com/jsdom/jsdom/issues/1330
- svg-path-properties, headless path measurement: https://www.npmjs.com/package/svg-path-properties
- flubber, path interpolation: https://www.npmjs.com/package/flubber

Renderer APIs, plugin behavior, and their engine-specific bugs change between releases; read the issue trackers before depending on a measurement or easing helper.

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

## Detection and source interpretation

- scikit-image measure API: https://scikit-image.org/docs/stable/api/skimage.measure.html
- scikit-image skeletonize: https://scikit-image.org/docs/stable/auto_examples/edges/plot_skeleton.html
- OpenCV contour hierarchy: https://docs.opencv.org/3.4.20/d9/d8/tutorial_py_contours_hierarchy.html
- OpenCV line segment detector: https://docs.opencv.org/4.9.0/db/d73/classcv_1_1LineSegmentDetector.html
- svgpathtools: https://pypi.org/project/svgpathtools/
- svgelements: https://github.com/meerk40t/svgelements
- shapely simplify: https://shapely.readthedocs.io/en/stable/reference/shapely.simplify.html
- potracer, raster vectorization: https://pypi.org/project/potracer/
- fontTools SVG path pen: https://fonttools.readthedocs.io/en/latest/pens/svgPathPen.html
- Whitebox shape complexity index: https://jblindsay.github.io/ghrg/Whitebox/Help/ShapeComplexityIndex.html
- Kazhdan shape descriptors: https://www.cs.jhu.edu/~misha/ReadingSeminar/Papers/Kazhdan04.pdf

These libraries and papers measure image and path properties; none of them judges whether a mark suits its brand. The version numbers in the URLs pin the documented API revision, not a version you are required to install.

## Source interpretation

- Official skill specifications define format and progressive disclosure; they do not prescribe a particular animation style.
- Official format specifications (SVG 2, Lottie, dotLottie) define the format and its arithmetic but never the aesthetic, so a numeric constant such as a dash period or easing rate read from a specification is authoritative while a duration taken from a tutorial or brand page is a precedent, not a rule.
- The detection libraries describe measurable image and path properties but supply no brand judgement, which is why a recommendation derived from a fingerprint is `inferred`, or `provisional` on a flattened raster, and never `observed`.
- The shape-complexity and symmetry literature supplies candidate metrics rather than thresholds; the complexity bands and symmetry cutoffs shipped in `references/technique-selection.md` are this package's own working bands and should be retuned against real projects.
- Brand pages are precedents, not universal rules. Extract principles such as restraint, narrative fit, and final-state clarity.
- Technical documentation is authoritative for renderer/codec behavior but may change; verify the installed version before relying on a flag or API.
- WCAG pages describe different conformance levels; do not label every recommendation as a universal legal requirement.
- Copyright and trademark rights remain with their owners. A reference does not grant permission to reuse its artwork, name, or footage.
