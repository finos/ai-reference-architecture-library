# Structurizr model

`ma_ref_arch_jan_2026/` is a Structurizr workspace for the [multi-agent reference architecture](../ma_ref_arch_jan_2026.md). It uses Structurizr's standard file names:

- `workspace.dsl` holds the model.
  - Layers are nested groups.
  - Each component lists its FINOS AI Governance Framework risks as a `risks` property and as one perspective per risk ID. In the Structurizr UI, choosing a perspective highlights every component affected by that risk.
  - RI-31 and RI-32 are not yet on `main` in `finos/ai-governance-framework`.
- `workspace.json` holds the diagram layout. Element positions are taken from `../assets/ma_ref_arch_jan_2026.drawio`.

`ma_ref_arch_jan_2026.png` is the exported diagram.

Structurizr is used here as an interim format before CALM, because this diagram began in draw.io and its layout had to be micromanaged to match. Diagrams that read well with automatic layout should use C4-PlantUML instead.

## View

The single **Overview** view shows every layer and relationship, arranged like the draw.io diagram:

- Amber arrows are telemetry into the Observability Layer.
- Purple arrows are evaluation and human oversight.
- Cross-layer arrows run through the gutters between layers.

To see which components a given risk affects, choose that risk's perspective in the Structurizr diagram viewer.

### Layout notes

- **Relationships connect components, not layers.** Structurizr can't draw an arrow to a group, so arrows between layers start and end at specific components. Telemetry, for example, comes from one representative component per layer.
- **Cross-layer arrows have hand-set bends** stored in `workspace.json`, laid in lanes spaced evenly across the gaps between layers. Structurizr's right-angle routing ignores boxes in its way, so add bends to any new cross-layer arrow and check the render for lines through boxes or labels.
- **An arrow's last segment always points at the target's centre.** Place the final bend so that segment doesn't cross a layer label.

## Editing

You need Java 21 or later and the Structurizr `.war` file from [docs.structurizr.com/binaries](https://docs.structurizr.com/binaries). To export images, use the `-playwright` build. Run the commands below from this folder.

To change the model, edit `ma_ref_arch_jan_2026/workspace.dsl`.

To change the layout, run Structurizr local on the workspace folder, then open http://localhost:8080 and the diagram editor (the pencil button):

```bash
java -Dstructurizr.datadirectory="$PWD/ma_ref_arch_jan_2026" -jar structurizr.war local
```

Notes on saving:

- **Saves are automatic.** About a second after you drag an element, the editor writes the new position to `workspace.json`. Arrow bends, label positions and `workspace.dsl` are left alone. To experiment without changing the real file, point `structurizr.datadirectory` at a copy of the folder.
- **The first save reformats the file.** The editor rewrites `workspace.json` in its own formatting and adds fields such as `lastModifiedUser` and `lastSavedView`, so expect a large diff the first time.
- **A `.structurizr/` working folder appears** in the workspace folder. It is ignored by the repository's `.gitignore`.

To re-export the PNG after editing, merge the saved layout into the DSL and export:

```bash
java -jar structurizr-playwright.war merge -w ma_ref_arch_jan_2026/workspace.dsl -l ma_ref_arch_jan_2026/workspace.json -o /tmp/merged.json
```

```bash
java -jar structurizr-playwright.war export -workspace /tmp/merged.json -format png -output /tmp/structurizr-png
```

The export writes `Overview.png`. Copy it over `ma_ref_arch_jan_2026.png`:

```bash
cp /tmp/structurizr-png/Overview.png ma_ref_arch_jan_2026.png
```

The first PNG export downloads a WebKit build for Playwright, about 80 MB.
