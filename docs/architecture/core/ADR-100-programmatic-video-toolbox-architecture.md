---
status: Draft
date: 2026-03-11
deciders:
  - aaronsb
  - claude
related: []
---

# ADR-100: Programmatic Video Toolbox Architecture

## Context

We built a single-file YouTube Poop generator (`llm_ytp.py`) that produces a complete animated video from Python — frame-by-frame rendering with Pillow, raw audio synthesis, ffmpeg assembly. It works, and it's fun. But the approach is rigid: every scene is a hand-rolled `for f in range(duration)` loop, effects are baked in, audio is disconnected from content, and there's no way to reuse pieces across projects.

The question: how do we evolve this into a general-purpose toolkit for producing programmatic video essays — the kind that explain complex ideas (graph structures, mathematical formulas, system architectures) through composed animation, synchronized narration, and parametric audio?

### Forces

- **Communication gap**: Complex technical ideas (attention mechanisms, knowledge graph grounding scores, electrical systems) are hard to convey in text. Animated visualization with narration makes them click.
- **Existing ecosystem**: Tools like Manim (3Blue1Brown), Motion Canvas, and Remotion exist but are either math-focused, JS-ecosystem-locked, or framework-heavy. None combine terminal replay + data viz + parametric audio + TTS narration in a Python toolbox.
- **Adjacent work**: The author has built related pieces across multiple projects — LaTeX rendering (texflow-mcp), live-coded music (strudel), knowledge graph visualization (kappa graph), terminal audio (playtui), educational simulators (split-phase), particle systems (snow, CellFlow).
- **Portability**: This should be a cloneable repo, not a service or MCP server. Clone it, write a script, render a video.

## Decision

Build a **Python toolbox for programmatic video production**, structured as a cloneable project template with composable modules:

### Core Abstractions

1. **Scene** — A unit of visual content with a duration. Produces frames. Scenes are composable (layered, sequenced, transitioned).
2. **Timeline** — Ordered sequence of scenes with transitions. The spine of a video.
3. **Layer** — Scenes stack. A narration layer, a visualization layer, an effects layer can run simultaneously.
4. **Effect** — Post-processing transform on frames (glitch, scanlines, chromatic aberration, fade, zoom). Chainable.
5. **AudioTrack** — Parametric audio (chords, drones, textures) or TTS narration, synced to timeline positions.

### Primary Rendering Backend: HTML/CSS/SVG → Headless Browser → Frames

The core rendering strategy is **web-native**: scenes are expressed as HTML, CSS, and SVG, then captured as frames via a headless browser (Playwright/Puppeteer). This plays to significant strengths:

- **CSS** provides gradients, `backdrop-filter`, `mix-blend-mode`, transforms, clipping, web fonts, proper typographic control — a richer visual language than any 2D drawing API
- **SVG** provides vector shapes, paths, curves, filters (`feGaussianBlur`, `feTurbulence`), and clean scaling
- **CSS variables** enable theming — swap a `theme.css` and the entire video changes aesthetic (dark terminal, clean whiteboard, glitch, paper)
- **React/Vue/vanilla JS** components become reusable scene templates — a `<FormulaScene>`, a `<GraphScene>`, a `<TerminalScene>`
- **Claude is exceptionally good at authoring HTML/CSS/SVG** — this makes the tool AI-native in a practical sense, not just as a gimmick

Each frame: render the scene's HTML at the target resolution → screenshot → save as PNG. Offline rendering means we don't care about browser performance — we care about visual quality.

### Scene Types (Renderers)

| Renderer | Implementation | Visual Capabilities |
|----------|---------------|-------------------|
| **Text** | HTML + CSS typography | Web fonts, gradients on text, animated reveals, kerning control |
| **Terminal** | asciinema `.cast` replay in HTML terminal emulator | Authentic terminal rendering with theme support |
| **Graph** | D3.js or vis.js in headless browser | Force-directed layouts, animated edges, node styling |
| **Formula** | KaTeX or MathJax in HTML | Publication-quality math rendering, inline with other content |
| **Chart** | D3.js / Chart.js / Observable Plot | Full interactive-quality charts rendered as frames |
| **Code** | Shiki or Prism.js syntax highlighting | Line-by-line reveal, region highlighting, diff views |
| **Diagram** | SVG shapes, paths, arrows | Architecture diagrams, flow charts, system visualizations |
| **Canvas** | Raw Pillow drawing | Escape hatch for pixel-level effects, glitch art, particle systems |

### Theming

CSS variables define the visual language of a video:

```css
/* theme-terminal.css */
:root {
  --bg: #0a0a0a;
  --fg: #00ff41;
  --accent: #ff3366;
  --font-mono: 'CaskaydiaCove Nerd Font', monospace;
  --font-display: 'Inter', sans-serif;
  --scanline-opacity: 0.08;
  --grain-intensity: 0.3;
}

/* theme-whiteboard.css */
:root {
  --bg: #fefefe;
  --fg: #1a1a1a;
  --accent: #2563eb;
  --font-mono: 'JetBrains Mono', monospace;
  --font-display: 'Source Serif Pro', serif;
  --scanline-opacity: 0;
  --grain-intensity: 0;
}
```

Same scene definition, different theme → different video aesthetic.

### Audio System

- **Parametric chords**: Define harmonic progressions tied to scene boundaries. Tension builds during complexity, resolution lands when concepts click.
- **Ambient textures**: Drones, filtered noise, bitcrushed layers — parameterized by scene mood/intensity.
- **TTS narration**: Script text rendered to audio via local TTS engine (Piper, F5-TTS, or Coqui XTTS). Synced to scene timing — scene durations can stretch to fit narration or narration can be paced to fit scenes.
- **Mix**: Layers mixed with per-track volume envelopes, ducking narration under music.

### Pipeline

```
Script (.py or .yaml)
  → Timeline (scenes + audio + narration)
    → Render scene HTML/CSS/SVG per frame
      → Headless browser screenshot → PNG sequence
        → Post-process (Pillow effects: glitch, aberration — when desired)
          → Generate/render audio tracks (parametric + TTS)
            → Composite: ffmpeg mux video + audio
              → Output .mp4
```

### What this is NOT

- Not a real-time engine. Offline rendering, quality over speed.
- Not a framework you inherit from. A library you import and call.
- Not opinionated about content. Works for YTP, explainers, data viz, art.

## Consequences

### Positive

- Complex ideas get a visual+audio communication channel that text and slides can't match
- Each renderer is independent — use only what you need
- The YTP we already built becomes ~30 lines against this toolkit instead of 575
- HTML/CSS/SVG as the rendering layer means Claude can directly author scenes with high visual quality
- Theming via CSS variables makes it trivial to restyle an entire video
- Web ecosystem gives access to D3, KaTeX, Shiki, and hundreds of other rendering libraries for free
- Parametric audio tied to scene semantics makes videos feel cohesive without manual scoring
- Clone-and-go: no infrastructure, no accounts, no services

### Negative

- Dependency surface grows: Node.js (headless browser), Playwright/Puppeteer, TTS engine, ffmpeg all need to be installed
- Audio synthesis from scratch is hard to make sound good — may need to iterate significantly on the parametric chord engine
- TTS quality varies by engine and voice — may need multiple backends
- Scene timing synchronization (especially narration-driven) adds real complexity

### Neutral

- The existing `llm_ytp.py` becomes the first "example project" built on the toolkit
- Could later add an MCP interface on top if desired, but the core stays library-shaped
- Strudel patterns could potentially be imported for the audio engine, bridging the music theory work

## Alternatives Considered

### Wrap Manim
Manim is excellent for math animation but is opinionated about its scene graph, rendering pipeline, and output format. Adding terminal replay, TTS, and parametric audio on top of Manim would mean fighting the framework more than using it. Better to learn from its design and build lean.

### MCP Server Architecture
An MCP server where Claude drives scene creation would be powerful for interactive authoring but adds deployment complexity, requires a running server, and locks the tool to Claude. A plain Python library is more universal — anyone can use it from any context, and Claude can drive it just fine via code generation.

### Use Remotion/Motion Canvas (JS ecosystem)
Both are capable but require Node.js/TypeScript. Remotion has a custom source-available license (free for individuals/small orgs, paid for companies with 4+ employees, mandatory telemetry from v5.0) — not suitable as the foundation of an open-source cloneable toolbox. Motion Canvas is MIT-licensed but less mature. The author's existing tooling (texflow, knowledge graph, whisper) is Python-native. Staying in Python for orchestration with a React rendering layer keeps things composable.

## Supporting Evidence

### Claude's Native Visual Generation (2026)

Anthropic's own product validates the HTML/CSS/SVG rendering approach. Claude's "inline visuals" feature ([claude.com/blog/claude-builds-visuals](https://claude.com/blog/claude-builds-visuals)) generates **HTML + inline SVG**, rendered in a sandboxed iframe running a Next.js app with React, Recharts, Mermaid.js, and Tailwind CSS. This is architecturally identical to cutscene's rendering pipeline.

Reverse engineering by [Reid Barber](https://reidbarber.com/blog/reverse-engineering-claude-artifacts) reveals the artifact system supports:
- `application/vnd.ant.react` — React components
- `text/html` — Single-file HTML pages
- `image/svg+xml` — SVG vector graphics
- `application/vnd.ant.mermaid` — Mermaid diagrams

The research predecessor, **"Imagine with Claude"**, went further: LLM-as-client, browser-as-server connected via WebSocket/JSON-RPC (effectively MCP), with raw HTML patched into the DOM via morphdom, and access to Chart.js, Google Maps, jsPDF, and html2canvas.

**Key takeaway**: Anthropic is actively investing in making Claude better at generating visual content as HTML/SVG/React. Building cutscene's rendering layer on this capability means betting on a trend the model provider is explicitly pushing — the capability will only improve over time.
