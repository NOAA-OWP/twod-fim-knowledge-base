## Description
After network modification removes/trims reaches at lakes (see [[DR-007 - How to Modify the Reach Network at Lakes]]), Flows2FIM still needs to assemble FIM across the lake. This decision is about how a lake is represented in the network and where its stage-derived rasters live.

## Alternatives

### ALT-A - Lake as a Regular Reach with `is_lake = True`

Add each lake to the network as a regular reach carrying an `is_lake = True` flag, so Flows2FIM treats it like any other reach during downstream-to-upstream assembly, with lake-specific behavior keyed off the flag. Flows2FIM would still need seed value for lakes, it is just that the FIM mosaicking for lakes will be added as a feature in Flows2FIM.

Stage-derived rasters for the lake are stored in the same results storage layout as reaches, indexed by stage rather than by flow. Illustrative layout:

```
results/
└── reach=12345/
    └── <hash(model_identity)>/        # runs filed under identity, not domain
        └── <hash(run_identity)>/      # solver; group/rollback by this
            └── z=283/f=0/
                ├── depth.tif           # COG, EPSG:5070; also hot-start seed
                ├── stl.geojson         # Stage Transfer Line
                ├── metadata.csv|parquet
                └── run.json            # self-describing run record (records domain used)
```

The negative of this approach is that it muddies the scope of Flows2FIM as lakes don't have any flows.
#### Open Questions
- Does a lake get a `reach_id` from an existing (removed) reach, or a newly minted id?
- Does the lake reach carry a geometry, and if so what (centerline through the pool, the dead pool polygon, a synthetic line)?
### ALT-B - Flows2FIM doesn't Cater Lake Reaches and Lakes are Treated as Breakpoints
#current
This alternative doesn't require any modification to Flows2FIM. Lake FIMs will be outside of F2F later with a simple lookup.

## Decision History
- 2026-05-28: ALT-B selected after discussion between engineers.
