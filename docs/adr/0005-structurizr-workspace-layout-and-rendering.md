# ADR-0005: Structurizr workspace folders and rendering workflow

**Status:** Proposed
**Date:** 2026-10-28
**Deciders:** AIGF maintainers
**Related:** [ADR-0002](0002-interim-diagram-formats-before-calm.md), [ADR-0006](0006-overview-diagram-styling-and-arrow-routing.md), [docs.structurizr.com](https://docs.structurizr.com)

## Context

Structurizr reads a model from `workspace.dsl` and saves diagram layout to `workspace.json`. These facts were checked with Structurizr 2026.09.19, the Java `.war` build:

- **The file names are fixed.**
  - The `local` diagram editor only looks for files named `workspace.dsl` and `workspace.json`. The names are constants in the `.war` (`WORKSPACE_DSL_FILENAME` and `WORKSPACE_JSON_FILENAME` in `AbstractWorkspaceAdapter`).
  - Only the folder it reads from is configurable, through the Java system property `structurizr.datadirectory`.
  - No command-line option for the folder was found. Starting `java -Dstructurizr.datadirectory=<folder> -jar structurizr.war local` was confirmed to load the workspace in that folder.
- **The older tools are archived.** Structurizr Lite, the Structurizr CLI and on-premises are archived on GitHub. Their functions are now commands of a single application: `local`, `validate`, `merge`, `export` and others.
- **Docker is optional.** The official quick start uses a Docker image, but the same application ships as a `.war` that needs only Java 21 or later. Builds are at [docs.structurizr.com/binaries](https://docs.structurizr.com/binaries), not as GitHub release assets.
- **PNG and SVG export needs the larger build.**
  - Only the `-playwright` build (about 430 MB) can export images. The plain build is about 220 MB.
  - The first image export downloads a WebKit browser (about 77 MB) into Playwright's cache, `~/Library/Caches/ms-playwright/` on macOS.
- **`merge` reapplies saved layout.** `merge -w workspace.dsl -l workspace.json -o merged.json` combines the model with the saved layout. It was checked to keep every element position, arrow bend and label position.
- **Export file names come from views.** `export -format png` writes `<view key>.png` and `<view key>-key.png` for each view.
- **Every export changes the PNG.** The footer of each PNG includes the export date, so the file is different every time even when the diagram is not.
- **The `local` editor saves layout to `workspace.json` automatically.** This was tested on 2026-10-28 by dragging one element in a copy of the multi-agent workspace.
  - On load, the editor showed the saved layout.
  - About a second after the drag, it wrote `workspace.json` without any save click.
  - Only the dragged element's position changed. All 14 hand-set arrow bends, every label position, the model and the styles were kept, and `workspace.dsl` was not touched.
  - `merge` then carried the new position through.
- **The first save from the editor is a noisy diff.** The editor rewrites `workspace.json` in its own formatting (spaces around colons, about 12% smaller). It also adds bookkeeping fields: `lastModifiedAgent` (an editor session ID), `lastModifiedUser` (a numeric ID), `lastSavedView` and `metadataSymbols`. These are harmless but change on every save.
- **The editor creates a `.structurizr/` working folder** in the workspace folder, holding a search index, logs and thumbnails. It is ignored in the repository's `.gitignore`.

The first arrangement used renamed files (`ma_ref_arch_jan_2026.dsl` and `.json`) for symmetry with the other files in the folder. Editing them in `local` then needed a temporary folder of symlinks with the standard names. That was awkward, and it was never tested whether saving in the editor writes through the symlink.

## Decision Drivers

- **No workarounds.** `local` should open a diagram directly.
- **One folder per diagram.** Room for more than one diagram under `structurizr/`.
- **Readable names.** The exported image should be named after the diagram, like the rest of the folder.

## Considered Options

### Option A: `workspace.dsl` and `workspace.json` directly in `structurizr/`

- Advantages: simplest.
- Disadvantages: only one diagram per folder, and the generic names don't match the diagram.

### Option B: Renamed files, opened through symlinks

- Advantages: names match the diagram.
- Disadvantages: needs a symlink workaround to edit, and it's untested whether saved layout writes back through a symlink.

### Option C: One folder per diagram, with the standard file names inside (chosen)

- Advantages: `local` points straight at the folder. Each diagram is self-contained.
- Disadvantages: one more folder level.

## Decision Outcome

**Option C:**

```
ra/
├── ma_ref_arch_jan_2026.md
├── assets/                             # draw.io source and its SVG export
└── structurizr/
    ├── README.md                       # how to edit and re-export
    ├── ma_ref_arch_jan_2026.png        # exported Overview view
    └── ma_ref_arch_jan_2026/
        ├── workspace.dsl               # the model
        └── workspace.json              # layout
```

To render the diagram, run these from `structurizr/`:

1. `java -jar structurizr.war validate -workspace ma_ref_arch_jan_2026/workspace.dsl`
2. `java -jar structurizr-playwright.war merge -w ma_ref_arch_jan_2026/workspace.dsl -l ma_ref_arch_jan_2026/workspace.json -o /tmp/merged.json`
3. `java -jar structurizr-playwright.war export -workspace /tmp/merged.json -format png -output /tmp/structurizr-png`
4. Copy `/tmp/structurizr-png/Overview.png` to `ma_ref_arch_jan_2026.png`.

To change the layout, run `java -Dstructurizr.datadirectory="$PWD/ma_ref_arch_jan_2026" -jar structurizr.war local` and drag elements in the editor.

### Comparing with the original

During development, a local HTML page showed the draw.io SVG and the exported PNG side by side, with zoom and pan kept in step. It is not committed, because it is a review aid, not reference content.

If you build one, open it from the file system in a normal browser, or take screenshots with headless Chrome. The Claude desktop app's built-in browser pane loads local HTML files inline, as `data:` URLs, so their relative image paths don't resolve.

## Consequences

- **New diagrams follow the same pattern:** `structurizr/<diagram>/workspace.{dsl,json}` plus `structurizr/<diagram>.png`.
- **Only commit a new PNG when the diagram changed.** Re-exporting always changes the date stamp in the footer.
- **The editor saves as you drag, so experiment on a copy.** There is no explicit save step. To try a layout without changing the real file, run `local` on a copy of the workspace folder.
- **Expect formatting churn in the first pull request after an editor save.** Later saves only change the moved positions and the bookkeeping fields.
