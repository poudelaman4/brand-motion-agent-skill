# Cliché and Restraint

Reject a move when it carries no brand-specific information, and spend motion only on what this mark alone can carry.

## Contents

- How a move becomes a cliché
- The cliché register
- Machine defaults
- Restraint doctrine
- When the answer is a fade
- When to ship static
- Surprise and consistency
- Failure modes
- QA

## How a move becomes a cliché

Read a move's stage before judging it; the stage fixes the remedy.

```text
1  innovation   means something, wins
2  diffusion    enters template libraries; born here
3  saturation   >1 brand per feed or sector
4  penalty      default use costs distinctiveness
```

Mark stage 2 as the birth point rather than stage 4. A move empties the moment a stock listing offers it to any brand, and a listing whose semantic range spans any feeling at all describes a move with nothing left to say.

Apply one rule: reject a move when it is available as a template and carries no brand-specific information. Judge age nowhere.

## The cliché register

Judge each row on brand specificity alone; refuse only the reflexive use.

| Move | Why it became one | Where it is dead | Replaces it with | Still acceptable when |
|---|---|---|---|---|
| Particle burst, dissolve, reassemble | Free in every particle system | B2B, financial, medical, premium | A build in true assembly order | The subject is literally particulate |
| Glitch, datamosh, RGB split | Digital shorthand, no content | Live streams, demos; reads as fault | Deletion, not replacement | Corrupted-data or archival content |
| Neon glow, node network | Connected-tech grammar, once real | Enterprise SaaS, banking, telco | One precise relationship, once | Mesh businesses selling the topology |
| 3D extrusion, chrome or gold | Pushed by render plugins | Everywhere; reads as 2008 broadcast | Flat, or diegetic 3D with mass | Jewellery, hardware, automotive, retro titles |
| The universal light sweep | Cheapest implication of premium | Everywhere; buys nothing | Revelation following construction | Optics, metals, paint; real reflection only |
| Bouncing letters | Default kinetic-type preset | Any word that is a name, not a joke | One shared baseline, reading order | Children's products, games, ≤6 characters |
| Draw-on applied to non-line-art marks | Trim Paths is one checkbox | Marks whose draw order misstates construction | An aperture from real geometry | Signatures, engraving, single-stroke monograms |
| Parts assembling from off-canvas | Buys complexity cheaply | Software; marks with a real assembly order | Assembly in true construction order | Multi-part lockups with genuine hierarchy |
| Mask wipe on every wordmark | Cheap, and always works | Any wipe ignoring the mark's geometry | An axis derived from the mark | Undrawnable wordmarks, one dominant axis |
| Zoom-through | Camera pushes past the mark | Anywhere the next thing is content | A hard cut, or real spatial transition | Brand-to-product surface navigation |
| Rotating 3D and orbit | Implies absent objecthood | Flat, financial, institutional | In-plane 15–45°, with a second reading | Automotive, hardware, 3D-first brands |
| Confetti | Celebration is free | Any professional-services or B2B surface | One authored gesture | Consumer celebration led by a character |
| Liquid morph on a solid mark | Default fluid-sim preset | Any mark that is not a liquid | Nothing; solids stay solid | Beverage, personal care, biotech, fluid marks |
| Ink bleed and paper as heritage | Nostalgia is a cheap register | Any brand with no material history | Archival material, cited specifically | A documented material past |
| Cinematic stinger with a whoosh | Sound buys feeling for free | Every deck opener, every second video | Design for silence; sonic spec | Broadcast titles, recurring sonic identity |
| Volumetric rays, depth of field, flare | Default cinematic preset | Anything flat or institutional | Real parallax and occlusion | Film, automotive, dioramic hero |
| Looping type that never resolves | Kinetics ships free | Any surface the user is reading | A loop returning to the mark | Loading state, signage, title run |
| The machine-default fingerprint | Different tools, one artefact | Any brand mistakable for a template | Motion by role plus one moment | One isolated occurrence, frequency-audited |

Record rejections in `forbidden_effects` in `intake-and-planning.md`, extending `contexts/premium-and-minimal.md`.

## Machine defaults

Treat these as an audit gate: they are this package's likeliest output. `[UNVERIFIED — thresholds borrowed from a public anti-pattern checklist, not a standard]`; hold them `provisional`.

| Pattern | Count that flags | Why it fails |
|---|---:|---|
| Uniform fade-in-up across components | ≥4 | Uniformity is the signature |
| Index-based stagger on a list | ≥2 lists | A linear delay means nothing was decided |
| Bounce on a utility action | any > 0 | A dropdown has no physical character |
| Blur on every entering element | ≥3 | A high-signal property, spent |
| Hover-scale with no discriminating context | ≥3 | A lift means nothing when all lift |
| Pulsing indicator, no documented rationale | any | Idle motion is noise |
| One easing curve across a whole view | 1 | One curve reads as printed |

State the law; no single pattern is the tell:

```text
The tell is the joint distribution: same transform on different rank,
same easing on different mass, same delay on different importance.
Differentiate by role, never by index.
```

## Restraint doctrine

Name five purposes, rank them unequally, and budget against the rank.

| Purpose | Motion budget | Failure when over-spent |
|---|---|---|
| Recognition | Low; legible by ~2.0 s | A memorable motion that delays recognition |
| Memory | Zero unless repeated | Cost with no return |
| Orientation | Moderate; high return, low ambition | A transition drawing attention to itself |
| Expression | Moderate, only at low frequency | A brand performing its personality every viewing |
| Function | Hard-capped, dull by design | Lying to the user about progress |

Resolve the conflict by rank: recognition and expression pull in opposite directions, and recognition always wins. Scale the budget inversely against frequency: expression at once-a-year, restricted at once-a-session, a ≤100 ms fade at dozens of daily viewings, no budget for a keyboard-initiated action.

## When the answer is a fade

Prefer a fade when any one of these holds:

- Seen more than ~20 times per month by the same person.
- Corporate, institutional, premium, or minimal register, per `contexts/premium-and-minimal.md`.
- Identity unresolved: positioning, palette, or type still moving.
- The static mark is itself weak.
- The animation competes with the message it introduces.
- Real estate is print, email signatures, PDF, documents.

Treat the fade as the answer, not a compromise, and as the only move normally surviving 1,000 viewings.

## When to ship static

Cap every mode, and require all four to collapse onto one still frame.

| Mode | Duration ceiling | Non-negotiable |
|---|---:|---|
| Loader or status | ≤2.0 s loop | Reads at 24 px; cheap; seamless at the seam |
| Reveal | ≤1.5 s | Legible by ~2.0 s; settles onto the still frame |
| Intro or stinger | ≤3.0 s | Ends before the viewer wonders when |
| Transition | ≤1.0 s | Interruptible |

Design that frame first, and require each mode to start and end on it. Ship it as the artefact landing in every screenshot, thumbnail, social preview, and favicon. `[UNVERIFIED as a standard — the most consistently cited practitioner figures; no standards body publishes them]`. Ship no animation when most placements are static: invoices, signatures, documents, PDF proposals.

## Surprise and consistency

Permit at most one surprise per system, and require it to recur. Author it as a named signature moment bound to one defined situation — a keynote ending, a successful payment, an annual-report cover — recognisable because it repeats. Reject any brand animating differently on every asset: that failure has a name, and it moves like a committee.

## Failure modes

### The template that reads as a template

**Symptom:** mark and motion swap for any other mark with no loss.
**Repair:** keep only where it names a referent; else use a pattern file or fade.

### Payoff after the look-away

**Symptom:** the resolving frame lands past ~2.0 s, after the reveal peaked.
**Repair:** settle earlier, shorten the stagger, hold ≥700 ms.

### The same motion on every element

**Symptom:** 4+ components share one transform, duration, easing, delay.
**Repair:** differentiate by role, then re-audit the counts.

### An ending by fade-out

**Symptom:** the sequence loses opacity to close.
**Repair:** land on the still frame, ship as 2× PNG with alpha.

### Committee drift

**Symptom:** two assets of one brand animate incompatibly.
**Repair:** publish the language in-tool, with locked easing.

## QA

- Freeze a random mid-frame; confirm it still reads as the approved mark.
- Locate the move's register row; reject unless a referent survives.
- Record machine-default counts as numbers, not adjectives.
- Diff the four modes for one pixel-identical still frame.
- Check every mode at 24 px and 200% zoom, on four backgrounds.
- Confirm a reduced-motion asset resolves to that same still frame.

Treat the four-stage cycle as `observed` and every count and ceiling as `provisional`; revise both against delivery feedback.
