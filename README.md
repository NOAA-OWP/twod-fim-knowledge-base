# 2D FIM Knowledge Base

Methodology and design notes for the 2D Flood Inundation Mapping (FIM) system
being developed for the Office of Water Prediction (OWP).

> [!NOTE]
>
> This is draft methodology for draft software developed for OWP by the NGWPC
> team led by Entarian. Further experiments, testing, quality control, and
> careful consideration are required before adopting this software.

## Contents

| Directory                                            | Purpose                                                                                              |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| [`system-decision-record/`](system-decision-record/) | Decisions, cases, experiments, and issues, recorded as [SDR](https://github.com/ar-siddiqui/sdr). The main body of work. |
| [`system-design/`](system-design/)                   | How the system is put together: the [design guide](system-design/guide.md) and the [reconciliation loop](system-design/reconciliation-loop.md). |
| [`solvers/`](solvers/)                               | Evaluation of 2D hydraulic solvers (LISFLOOD-FP, SFINCS).                                            |
| [`qgis/`](qgis/)                                     | QGIS project template, styles, and startup scripts for viewing outputs.                              |

## Reading it

The decision record is published as a browsable site:

**https://ngwpc.github.io/twod-fim-knowledge-base/**

It is also an [Obsidian](https://obsidian.md) vault — open
`system-decision-record/` as a vault to get bidirectional links and graph view.
Start at [the Decision Register](system-decision-record/02_Decisions/Decision%20Register.md).

## Contributing

Add a new record by copying the numbering and front matter of an existing one
in the same folder. Link related records with `[[wikilinks]]` so they show up in
the graph. The site rebuilds on push to `main`.