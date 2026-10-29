# ADR-0001: Record architecture decisions

**Status:** Proposed
**Date:** 2026-10-28
**Deciders:** AIGF maintainers
**Related:** [ADR index](README.md), [finos/ai-governance-framework#429](https://github.com/finos/ai-governance-framework/pull/429)

## Context

Reference architectures in this library are increasingly drawn and maintained with an AI agent's help. Many choices behind a diagram are not visible in the files themselves: which tools were tried and why they failed, what each tool can and cannot do, and which shortcuts were rejected. Without a record, each new contributor, person or agent, rediscovers the same limits by trial and error.

This library is being rolled into the AI Governance Framework (AIGF). AIGF is adopting ADRs in [finos/ai-governance-framework#429](https://github.com/finos/ai-governance-framework/pull/429). These ADRs follow that format, so they can move into AIGF's series when the library does.

## Decision Drivers

- **Avoid repeated discovery.** A future contributor should learn in minutes what took hours to find.
- **Explain the files.** Someone looking at an unusual layout or file name should be able to find out why it is that way.
- **Stay lightweight.** Recording a decision should take less effort than rediscovering it.

## Considered Options

### Option A: Notes in each diagram's README

- Advantages: next to the files they describe.
- Disadvantages: decisions that span several diagrams or tools have no single home. READMEs describe how to use files, not why they are built that way.

### Option B: Architecture Decision Records in `docs/adr/` (chosen)

One short Markdown file per decision, numbered in order, using the same format as the ADRs in `finos/ai-governance-framework`.

- Advantages: a familiar format, and one place to look. Each decision can be superseded without rewriting history.
- Disadvantages: one more folder to keep current.

## Decision Outcome

**Option B.** Each ADR has:

- a numbered title;
- a status (Proposed, Accepted, Superseded or Deprecated), date, deciders and related links;
- sections for Context, Decision Drivers, Considered Options, Decision Outcome and Consequences.

ADRs record facts that were checked, and say plainly when something was not tested.

## Consequences

- New ADRs are numbered after the highest existing number and listed in [README.md](README.md).
- When a decision changes, write a new ADR that supersedes the old one, and update the old one's status. Do not rewrite it.
- **When this library moves into AIGF,** move these ADRs into AIGF's `docs/adr/`. Renumber them after AIGF's own ADRs, drop this ADR-0001 in favour of AIGF's, and update the links between them.
