# ADR-0004: Risk IDs on diagram components

**Status:** Proposed
**Date:** 2026-10-28
**Deciders:** AIGF maintainers
**Related:** [ADR-0002](0002-interim-diagram-formats-before-calm.md), [ADR-0003](0003-plantuml-layout-matching-experiment.md), [finos/ai-governance-framework risk catalogue](https://github.com/finos/ai-governance-framework/tree/main/docs/_risks)

## Context

The FINOS AI Governance Framework (AIGF) catalogues AI risks as RI-N items. Its diagram `diagrams/agentic-skill-system_v1-with-risks.puml` labels each component with the risks that apply to it. The same overlay was wanted for the multi-agent reference architecture.

The mapping of risks to components is a judgment based on each risk's summary in the AIGF catalogue. It has not been reviewed by the people responsible for those risks.

These facts about the catalogue were true on 2026-10-28:

- **RI-1 to RI-29:** on `main` in `finos/ai-governance-framework`, under `docs/_risks/`. Some numbers are unused.
- **RI-30, RI-31 and RI-32:** only on unmerged branches. RI-30 is Skill/Plugin Supply Chain Compromise; RI-31 is Human Approval Fatigue and Consent Gate Degradation; RI-32 is Third-Party Content Loaded as Agent Instructions.
- **RI-30 is not used.** "Skills-based routing" in this architecture means sending a request to an agent with the right capability. It does not mean loading third-party skill or plugin bundles, which is what RI-30 is about.
- **RI-31 and RI-32 are used.**
  - RI-31 is on the human-in-the-loop components: Application and Human Supervision.
  - RI-32 is on MCP Client and MCP Zoo, because MCP tool descriptions are third-party text loaded into the agent's instructions.

## Decision Drivers

- **Queryable.** Tools should be able to find every component affected by a given risk.
- **Visible.** People reading the diagram should see the risks without a separate tool.
- **One source of truth.** The mapping should live in one place.

## Considered Options

### Option A: Risk IDs as text in each box's description

- Advantages: visible in any rendering, and the only option in PlantUML.
- Disadvantages: not queryable, and it crowds the boxes.

### Option B: Structurizr properties plus one perspective per risk (chosen for Structurizr)

Each component gets a `risks` property, for example `"RI-24, RI-28"`, and one perspective per risk ID whose description is the risk's title.

- Advantages: in Structurizr's diagram viewer, choosing a perspective highlights every affected component, so the overlay is data. The boxes stay uncluttered.
- Disadvantages: invisible in a static PNG unless a perspective is selected before export.

### Option C: A separate risk view

- Advantages: a focused picture for risk reviewers.
- Disadvantages: perspectives already provide this, and a separate view of the multi-agent diagram turned out sparse and unhelpful (see [ADR-0006](0006-overview-diagram-styling-and-arrow-routing.md)).

## Decision Outcome

**Option B.** The mapping lives only in `structurizr/ma_ref_arch_jan_2026/workspace.dsl`.

The C4-PlantUML experiment ([ADR-0003](0003-plantuml-layout-matching-experiment.md)) used Option A, and was not kept. It also drew two notes about risks that come from how components connect, not from any single component. They aren't in the Structurizr model, but are worth adding to the reference architecture's text:

- **Cross-agent propagation (RI-28, RI-27):** shared state, memory and handoff let one compromised agent affect every agent that reads the same state. Poisoned long-term memory makes the effect last across sessions.
- **Feedback-loop poisoning (RI-9, RI-27):** feedback drives Adaptive Learning, which rewrites prompts, agent configuration and tool selection. Unvalidated or adversarial feedback becomes a lasting change to agent behaviour.

## Consequences

- **Track RI-31 and RI-32.** If those branches are not merged, remove both IDs from the DSL. If they are renumbered, update them.
- **Update risk titles.** The perspective descriptions copy each risk's title, so update them if the AIGF retitles a risk.
- **Review the mapping.** It should be reviewed by AIGF risk owners before the diagram is presented as authoritative.
- **Carry the mapping into CALM.** When the diagram moves to CALM ([ADR-0002](0002-interim-diagram-formats-before-calm.md)), the per-component risk IDs are the part most worth keeping, as CALM controls or metadata. How they map onto CALM controls has not been worked out.
