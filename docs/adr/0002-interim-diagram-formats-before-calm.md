# ADR-0002: PlantUML or Structurizr as interim formats before CALM

**Status:** Proposed
**Date:** 2026-10-28
**Deciders:** AIGF maintainers
**Related:** [ADR-0003](0003-plantuml-layout-matching-experiment.md), [ADR-0004](0004-risk-ids-on-diagram-components.md), [ADR-0005](0005-structurizr-workspace-layout-and-rendering.md), [ADR-0006](0006-overview-diagram-styling-and-arrow-routing.md), [FINOS CALM](https://calm.finos.org), [finos/architecture-as-code](https://github.com/finos/architecture-as-code), [#42](https://github.com/finos/ai-reference-architecture-library/issues/42)

## Context

FINOS CALM (Common Architecture Language Model) is FINOS's architecture-as-code standard. It models nodes, relationships, controls and metadata, and it is where reference architectures in this library should end up. [#42](https://github.com/finos/ai-reference-architecture-library/issues/42) already proposes codifying the multi-agent reference architecture in CALM.

Many contributors reach for a familiar diagrams-as-code format before they have learned CALM or are ready to use its tooling. Two such formats were used for the multi-agent reference architecture, [ma_ref_arch_jan_2026.md](../../Library/reference_architecture/agentic_ai/multi_agent/ra/ma_ref_arch_jan_2026.md):

- **C4-PlantUML.** Strong ecosystem support: preview and editing extensions in VS Code, and renderers in most documentation tools. The FINOS AI Governance Framework's own diagrams use it, for example `ai-governance-framework/diagrams/agentic-skill-system_v1-with-risks.puml`. PlantUML places boxes automatically with a layout engine, Graphviz by default.
- **Structurizr DSL.** The reference implementation of C4, maintained by C4's creator. It saves exact element positions, arrow bends and label positions in `workspace.json`, so nothing is left to an automatic layout engine.

The multi-agent diagram began in draw.io (`assets/ma_ref_arch_jan_2026.drawio`, exported to `.svg`). draw.io and PowerPoint give full control over layout, but they can't carry risk tagging as data, and their files are hard to review in a pull request. The goal was a text version that kept the draw.io arrangement readers already knew, and added the FINOS AI Governance Framework risks for each component ([ADR-0004](0004-risk-ids-on-diagram-components.md)).

### What was learned from the multi-agent diagram

- **C4-PlantUML, Graphviz layout.** Graphviz placed the layers in a different order from the draw.io diagram, and hand-tuning layout hints kept flipping the result.
  - Hints that one box should sit beside another (`-[hidden]right->`) are often ignored when the two boxes are in different boundaries.
  - Matching the draw.io arrangement took an automated search: 648 variants, each rendered and scored against 14 placement checks.
  - Adding a single arrow (Feedback → Adaptive Learning) broke the layout in all six ways it was tried.
  - Details are in [ADR-0003](0003-plantuml-layout-matching-experiment.md).
- **PlantUML with the ELK layout engine** (`!pragma layout elk`). It ignored the layout hints and stacked the diagram into a single column, 954 × 3762 pixels.
- **Structurizr DSL.** Element positions were taken from the draw.io file, and the arrangement was reproduced exactly on the first render. Cross-layer arrows were then routed by hand ([ADR-0006](0006-overview-diagram-styling-and-arrow-routing.md)).

None of this means PlantUML is a poor choice in general. The trouble came from requiring the layout to match an existing picture.

### CALM's layout support today

This was checked by reading the source of `finos/architecture-as-code` on 2026-10-28, not by running the tools:

- **The format has no layout.** A CALM file has no coordinates. CalmStudio's design notes say imported CALM files have no positions, which is why it lays them out automatically with ELK.
- **The VS Code extension saves box positions.**
  - Its visual editor writes each node's `x`, `y`, and optionally width and height, into the CALM file under `metadata._layout`, and reapplies them on load (`calm-plugins/vscode/src/webview/transforms/calm-editor-transformer.ts`).
  - It saves no arrow bends, label positions or styles.
  - `_layout` is the extension's own convention inside free-form metadata, not part of the CALM specification.
  - The code was last changed on 2026-10-20; whether a released version includes it was not checked.
- **CalmStudio lays out automatically.** It uses ELK, with a re-layout action. Its `.calmstudio.json` sidecar file holds extension-pack metadata, not positions (`calm-studio/apps/studio/src/lib/io/sidecar.ts`). Its MCP server's view tool writes ELK-computed positions to that sidecar. No code was found that saves boxes dragged by hand.
- **The experimental calm-explorer** uses automatic Dagre layout only.

### Other formats considered but not tried

- **Mermaid flowcharts.** Mermaid ignores a subgraph's own direction setting when any of its nodes links outside the subgraph. Mermaid `block` diagrams use explicit grid placement and render inline on GitHub, but were not prototyped.
- **D2 with grid containers** (`grid-rows` / `grid-columns`). Explicit grid placement. Not prototyped.
- **Raw Graphviz DOT.** It exposes options PlantUML hides, such as `newrank=true` and `constraint=false`. It is still an automatic layout. Not prototyped.

## Decision Drivers

- **A path to CALM.** Interim formats should not get in the way of moving to CALM later.
- **Low barrier to entry.** Contributors should be able to start with tools they already know.
- **Readable diagrams.** The picture must be easy to understand.
- **Faithful to the original, when there is one.** A diagram that began in draw.io or PowerPoint should still look like that original.
- **Risks as data.** Risk IDs should be attached to components, not only drawn on a slide.

## Considered Options

### Option A: Always use C4-PlantUML

- Advantages: familiar, well supported in VS Code, and the same notation as the governance framework's diagrams.
- Disadvantages: the layout engine decides placement. Matching an existing picture needs fragile tricks.

### Option B: Always use Structurizr

- Advantages: exact, predictable layout. Risks can be modelled as perspectives.
- Disadvantages:
  - Needs Java 21 or later and a large `.war` file (about 430 MB for the build that exports PNGs).
  - `workspace.json` produces noisy diffs.
  - Hand-placing every box is wasted effort when automatic layout already reads well.

### Option C: Choose per diagram, by whether the layout must be micromanaged (chosen)

- Advantages: the simple, well-supported format by default; exact layout only where it's needed.
- Disadvantages: two interim formats to know. Contributors need a rule for choosing between them, given below.

### Option D: Require CALM now

- Advantages: one format, the FINOS standard, with controls and metadata as first-class data.
- Disadvantages: a higher barrier for contributors who don't yet know CALM. Its tools save box positions at best, never arrow routing, so a diagram that must match an existing picture can't be reproduced yet.

## Decision Outcome

**Option C.** CALM is the target format. Until a contributor is ready to use CALM and its tooling, choose an interim format as follows:

- **C4-PlantUML** when the available layout engines produce a diagram that is easy to understand. This is the usual case for new diagrams, and for diagrams whose arrangement doesn't have to match an existing picture.
- **Structurizr** when the layout needs to be micromanaged to reflect a diagram that began in a tool without risk tagging, such as draw.io or PowerPoint.

**A practical test:** render the diagram with C4-PlantUML first. If the result reads well, stop there. Switch to Structurizr if any of these happen:

- you need more than a few hidden layout hints;
- small edits flip the arrangement;
- an arrow can't be added without breaking the layout.

**Applied to the multi-agent reference architecture:** it began in draw.io, and its layout had to be micromanaged to match. So the Structurizr model in `structurizr/ma_ref_arch_jan_2026/` is its diagram-as-code version, laid out as described in [ADR-0005](0005-structurizr-workspace-layout-and-rendering.md). A C4-PlantUML version was tried first and not kept ([ADR-0003](0003-plantuml-layout-matching-experiment.md)). The draw.io file remains the visual reference that element positions are derived from.

## Consequences

- **Either way, plan for CALM.** Name components and relationships so they map cleanly to CALM nodes and relationships, and keep risk IDs attached to components so they can become CALM controls or metadata later. That mapping has not been tried.
- **Structurizr quirks**, learned on the multi-agent diagram:
  - **No arrows to groups.** Relationships connect elements, not groups. Arrows from one whole layer to another become arrows between specific components; for example, telemetry comes from one representative component per layer.
  - **Unique names.** Container names must be unique within a software system. The three "Guardrails / Policies" boxes are named Agent, MCP and LLM Guardrails / Policies.
  - **Outer boundary.** A C4 container view needs a software system, so every component sits inside a "Multi-Agent Platform" boundary that the draw.io diagram doesn't have.
- **Revisit this rule** in any of these cases:
  - a CALM tool starts saving arrow bends;
  - `_layout`, or something like it, becomes part of the CALM specification;
  - contributors become comfortable enough with CALM to start there.
- **CALM and Structurizr could coexist,** with CALM as the model and risk data and Structurizr as the curated picture. No converter between the two was found, so keeping them in step would be extra work.
