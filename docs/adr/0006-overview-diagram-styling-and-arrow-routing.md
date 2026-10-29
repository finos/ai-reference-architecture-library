# ADR-0006: Overview diagram styling and arrow routing

**Status:** Proposed
**Date:** 2026-10-28
**Deciders:** AIGF maintainers
**Related:** [ADR-0002](0002-interim-diagram-formats-before-calm.md), [ADR-0005](0005-structurizr-workspace-layout-and-rendering.md)

## Context

The Structurizr Overview of the multi-agent architecture shows 38 components in nested layer groups, and 39 relationships. Several arrows cross layers: telemetry into the Observability Layer, and Evaluation feeding back into the runtime. Drawn straight, those arrows cut through unrelated boxes. Several approaches were tried.

### What was tried, and what happened

- **Focused views.** The cross-layer arrows were first moved into separate Oversight and Telemetry views, which reused the Overview positions but showed only the components involved. Once the Overview carried those arrows itself, the focused views looked sparse and added nothing, so they were removed. Perspectives ([ADR-0004](0004-risk-ids-on-diagram-components.md)) are the better way to focus on part of the diagram.
- **Right-angle routing (`routing Orthogonal`).** Structurizr's right-angle routing ignores obstacles, so lines ran through unrelated boxes. Explicit arrow bends with `routing Direct` worked.
- **Dashed grey telemetry arrows.** These looked like the dotted grey layer borders, especially where they bent at right angles next to a border. A reviewer found the diagram confusing.
- **Narrow gutters.** With the original spacing, some arrows ran within about 20 pixels of the MCP and LLM layer borders and looked like they passed through those layers.

## Decision Drivers

- **One readable picture.** Every relationship visible in a single diagram, with no line through a box or a layer label.
- **Unambiguous styles.** A layer border, a data-flow arrow, a telemetry arrow and an oversight arrow must each look different.
- **Faithful to the draw.io layout.** The draw.io arrangement is kept, though gutters may be widened.

## Decision Outcome

### Element positions

Positions come from the draw.io file:

- Each element's centre is the draw.io cell's centre, scaled ×2.4 in both directions.
- Boxes are 340 × 100 pixels; the person shape is 300 × 300.

Whole layers were then moved apart to widen the gutters:

| Moved | By |
|---|---|
| Knowledge Layer | 150 px left |
| MCP and LLM Layers | 240 px right |
| Tools Layer and Long-Term Memory | 90 px right |
| Observability Layer | 180 px down |
| Evaluation Layer | 330 px down |

A group's border sits 50 pixels outside its outermost elements on the top, left and right, for each level of nesting. The bottom edge sits about 113 pixels below, because the group's label is at the bottom-left. This was checked against an SVG export, and gutter positions can be worked out from it.

### Arrow routing

- **Bends are saved in `workspace.json`.** Cross-layer arrows have explicit bends (`vertices`) stored in the Overview view, with `routing Direct`.
- **Lanes are evenly spaced.** Each gutter's lanes are spread evenly between the two layer borders, not stacked at fixed offsets. The gutters are:
  - between the Knowledge and Agent Layers;
  - between the Agent Layer and the MCP/LLM Layers;
  - between the Agent and Observability Layers;
  - between the Observability and Evaluation Layers;
  - between the Collaboration Patterns box and the runtime.
- **The last segment always aims at the target's centre.** Place the final bend so that segment doesn't cross a label. For example, both arrows into Events come up the gap to its right, because from below they would cross the "Observability Layer" label.
- **Labels can be moved along their arrow.** A relationship's `position` (percent along the line) moves its label off crowded segments.
- **Some crossings are unavoidable.** For example, the Knowledge Layer sits left of the left-gutter lanes, so its telemetry arrow must cross them. Crossings are acceptable; lines through boxes or labels are not.

### Styles

| Thing | Style |
|---|---|
| Layer groups | Solid, light grey (`#c4c4c4`), 3 px |
| Ordinary relationships | Solid, dark grey, direct |
| Telemetry (tag `Telemetry`) | Solid, amber (`#d9822b`), 2 px. No label; the signal types are in a `signals` property |
| Oversight (tag `Oversight`) | Solid, purple (`#7d3c98`) |

### Telemetry

There is one representative telemetry arrow per layer, following the markdown's "Relationship to Other Layers" section:

| From | To |
|---|---|
| Application | Logs |
| Gateway | Events |
| Secure Execution | Traces |
| Vector DBs | Metrics |
| MCP Gateway | Events |
| LLM Gateway | Metrics |
| Runtime Protection | Events |

## Consequences

- **Adding an arrow that crosses layers:** give it a lane in the right gutter, spaced evenly with the others, and check the render for lines through boxes or labels.
- **The positioning scripts are not in the repo.** The draw.io conversion and gutter calculations were done with one-off scripts. From now on, change the layout in Structurizr local, or edit `workspace.json` following the rules above.
- **The arrow colours appear only in the diagram key.** The exported `Overview-key.png` shows them but is not committed. If readers need the colours explained, add a legend to the README.
