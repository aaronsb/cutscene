---
status: Draft
date: 2026-03-11
deciders:
  - aaronsb
  - claude
related:
  - ADR-100
---

# ADR-101: Scene Composability and Project Structure

## Context

ADR-100 defines the pipeline (Python orchestrator → React renderer → Playwright capture → ffmpeg). But it doesn't address what a cutscene *project* looks like on disk — how scenes relate to each other, how styling flows through a video, and how the whole thing behaves as a git-managed artifact.

The goal is: **reusable blocks that can be edited and composed, relevant to each other with shared styling, all checked into git.** A cutscene project should be diffable, reviewable, branchable, and PRable — just like code.

### Forces

- Scenes aren't independent — they share visual language (colors, typography, spacing), reference the same data, and build on each other narratively
- Videos evolve over time — you revise a scene, adjust timing, swap a theme. This needs to be trackable in version control.
- A scene component authored for one video should be reusable in another without copy-paste
- Claude (or any AI) authoring scenes needs a well-defined, small API surface — not "write arbitrary React"
- The project structure should be self-evident — clone the repo, look at the directory, understand what's what

## Decision

### Project Structure

A cutscene project is a directory (typically a git repo) with this layout:

```
my-video/
  cutscene.yaml             ← project config: resolution, fps, theme, TTS engine
  timeline.yaml             ← scene sequence, transitions, timing, audio cues
  scenes/
    01-intro.tsx             ← React components, one per scene
    02-terminal-demo.tsx
    03-graph-walkthrough.tsx
    shared/                  ← reusable sub-components
      GraphNode.tsx
      CodeBlock.tsx
      AnimatedFormula.tsx
  themes/
    default.css              ← CSS variables defining the visual language
    terminal-green.css
    whiteboard.css
  narration/
    script.md                ← narration text keyed to scene IDs
  audio/
    chords.yaml              ← parametric chord/drone definitions per scene
  assets/                    ← static assets (images, cast files, data)
    demo.cast
    graph-data.json
  dist/                      ← render output (gitignored)
    output.mp4
```

### Scene Components

Each scene is a React component that receives **frame props** from the Python orchestrator:

```tsx
// scenes/03-graph-walkthrough.tsx
import { SceneProps } from 'cutscene';
import { GraphNode, GraphEdge } from './shared/GraphNode';

export default function GraphWalkthrough({ frame, progress, theme }: SceneProps) {
  // progress: 0..1 over scene duration
  // frame: absolute frame number within this scene
  // theme: resolved CSS variable values

  const visibleNodes = Math.floor(progress * nodes.length);

  return (
    <div className="scene graph-scene">
      <h1 style={{ opacity: Math.min(1, progress * 3) }}>
        Knowledge Graph
      </h1>
      <svg viewBox="0 0 1280 720">
        {nodes.slice(0, visibleNodes).map(n => (
          <GraphNode key={n.id} {...n} />
        ))}
      </svg>
    </div>
  );
}
```

Scenes receive minimal, well-defined props. They don't manage their own timing — the orchestrator does. They render one frame's worth of visual state.

### Shared Components

Reusable building blocks live in `scenes/shared/`. These are the vocabulary of the toolkit:

- `<GraphNode>`, `<GraphEdge>` — knowledge graph elements
- `<CodeBlock>` — syntax-highlighted code with line highlighting
- `<Formula>` — KaTeX-rendered math
- `<TerminalReplay>` — asciinema cast playback
- `<TypewriterText>` — text that appears character by character
- `<ProgressBar>`, `<Annotation>`, `<Arrow>` — callouts and indicators

A cutscene project can import from the cutscene toolkit's built-in components or define its own in `scenes/shared/`.

### Theme System

Themes are CSS files that define variables. Every built-in component and scene template references these variables:

```css
/* themes/terminal-green.css */
:root {
  /* Surface */
  --cs-bg: #0a0a0a;
  --cs-bg-elevated: #1a1a1a;
  --cs-surface: #0d1117;

  /* Text */
  --cs-fg: #00ff41;
  --cs-fg-muted: #4a8f5c;
  --cs-heading: #33ff66;

  /* Accents */
  --cs-accent: #ff3366;
  --cs-accent-2: #ffcc00;

  /* Typography */
  --cs-font-mono: 'CaskaydiaCove Nerd Font', monospace;
  --cs-font-display: 'Inter', sans-serif;

  /* Effects */
  --cs-scanline-opacity: 0.08;
  --cs-grain-intensity: 0.3;
  --cs-glow-color: rgba(0, 255, 65, 0.15);
}
```

All variables prefixed `--cs-` to avoid collisions. Changing `cutscene.yaml` to point at a different theme re-skins the entire video.

### Timeline

The timeline is declarative YAML — the orchestrator reads it and drives everything:

```yaml
# timeline.yaml
scenes:
  - id: intro
    component: scenes/01-intro.tsx
    duration: 3s
    narration: "Let me show you how a knowledge graph works."
    chord: Cmaj7
    transition_in: fade

  - id: terminal
    component: scenes/02-terminal-demo.tsx
    duration: 5s
    narration: "First, we ingest a document."
    chord: Am7
    props:
      cast_file: assets/demo.cast

  - id: graph
    component: scenes/03-graph-walkthrough.tsx
    duration: 8s
    narration: "Watch how concepts connect."
    chord: [Dm7, G7, Cmaj7]  # tension → resolution
    props:
      data: assets/graph-data.json
      highlight: ["grounding-score"]

transitions:
  fade:
    type: crossfade
    duration: 0.5s
```

### Composability Rules

1. **Scenes are pure functions of props** — given the same frame number and data, they render the same output. No side effects, no internal state.
2. **Shared components are the reuse mechanism** — not scene inheritance, not mixins. A `<GraphNode>` used in scene 3 is the same component in scene 7.
3. **Themes flow down** — CSS variables set at root, every component inherits. No per-component color overrides unless intentional.
4. **Timeline owns timing** — scenes don't know their own duration. The orchestrator says "you're at progress 0.42" and they render that state.
5. **Data is external** — graph data, terminal casts, code snippets live in `assets/`. Scenes reference them via props.

### Git Workflow

Since everything is files:

- `git diff scenes/03-graph-walkthrough.tsx` — see how a scene changed
- `git log --oneline timeline.yaml` — see how the structure evolved
- Branch for experiments: `git checkout -b try-whiteboard-theme`
- PR a scene rewrite, review the diff
- Tag releases: `git tag v1.0` for the published cut

## Consequences

### Positive

- Every aspect of a video is version-controlled and reviewable
- Scenes compose through shared components, not copy-paste
- Theme swaps are one-line config changes
- AI agents author against a small, well-defined surface (SceneProps + shared components + CSS variables)
- Project structure is self-documenting
- Multiple people (or agents) can work on different scenes in parallel on branches

### Negative

- React/TypeScript dependency for scene authoring — authors need JSX (though AI generates it well)
- Tight coupling between scene filenames and timeline references — renaming a file means updating timeline.yaml
- Shared components need careful design to be genuinely reusable without over-abstraction

### Neutral

- The `llm_ytp.py` proof of concept becomes React components; glitch/scanline effects move to CSS filters or post-processing
- Narration format (markdown, SRT-like, plain text keyed by scene ID) needs its own decision
- Audio chord spec (how progressions map to scene boundaries) needs its own decision

## Alternatives Considered

### Flat script approach (like llm_ytp.py)

Write everything in one Python file with imperative drawing code. Works for one-offs but scenes can't be reused, themes don't exist, and nothing composes. The YTP proved the concept but also proved the limits.

### Template-based (like SyncCast's Visual Atoms)

Pre-built scene types selected by name with data parameters. Simpler to author but limits expressiveness — you can only use the templates that exist. Custom visuals require extending the template library rather than just writing a component.

### Markdown/YAML-only (no code in scenes)

Define everything declaratively — no TSX, no code. Maximally AI-friendly but too constraining for complex visualizations. A graph animation with custom layout logic can't be expressed in pure YAML. Code-in-scenes (React components) is the right trade-off between expressiveness and structure.
