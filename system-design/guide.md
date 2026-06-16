## Guiding Requirements

- Run any single reach end-to-end on a developer laptop
- Mix and match minor updates
- Flexibility to add scenarios
- Flexibility to update model domain
- Flexibility to alternate between different solvers per reach

## Key Design Principles

- The System is designed with database as the brain plus orchestrator as a reconciliation loop
- Orchestrator has main goal of reconciling current state towards desired state
- The reconciliation loop is borrowed from Kubernetes; it makes the system self-healing. A controller watches S3 and forms the current state; when it sees a difference between current_state and desired_state it acts, then writes what it observed back into current_state, then watches again. The loop never stops.
- Jobs are stateless, they intake JSON, output JSON. They write to S3
- Jobs do not interact with Database
- Orchestrator is the sole writer/editor to deployed system, no external updates are allowed
- User updates come through override system
- Deployed system does not entertain testing, testing should be carried out separately and desired state must be updated via overrides or updates to desired state table
- Inputs are versioned
- Outputs are immutable and stored at addressed paths (A rerun with same inputs will overwrite the old content)
- As orchestrator try to bridge gap between current state and desired state it skips what already exist and runs only the gap between two states. This is done through addressed paths.
- If the desired state changed and existing outputs become stale, they are handled by S3 lifecycle policies
- Self documenting paths
- Operational Unit is per reach folder. Someone can `aws s3 sync` one reach to a laptop and have everything to inspect or rerun
- Stateless code i.e. function shaped, no load-mutate-save lifecycle
- What can be derived, will not be stored beyond some days on S3
- Desired state should be preserved at all cost as it will update as system would self update as well as updates from external users

## Key Design Decisions

- STL is not part of model definition, but STL will inform model_domain desired state
- Model = identity (reach + sources + grid/CRS + params) + realization (domain). The `build_model` software version is recorded as provenance (`current_state.build_model_version`), not folded into `identity_hash`, so a software bump can drive a selective rebuild without changing the content-addressed path.
- Run = run_identity (engine + engine version) + realization (scenario: q, kwse)
- Identity and realization are always separate component in hashes and separate DB columns so that group / roll back / delete by either is possible
- Runs with same identity_hash stay valid even if a domain change updates the model_id
- The database has three main tables
- Desired state = input to system = authored intent
- Current state = what's actually been achieved = current state of the system
- Runs = the per-run record (ledger)
- Some desired_state fields are nullable — NULL means "use the default source", a value means it is authored. current_state always holds the effective value. This separation makes it clear that there is one place to author anything, one place place to read what's live.
- Rollback = revert desired state; content-addressing reuses prior outputs if not yet aged out, else will be recomputed

![alt text](guide-diagrams/system-landscape.drawio.png)

## Versioning Model

- When we store in S3 we store by repo version, (minor updates can live together, but major can not)
- Each version is pinned to a commit in SDR

## Conceptual Modeling Objects

This is conceptual model of different objects in modeling, this is not a working database schema, neither these are Python data classes.

### Reach (id: reach_id)
- reach_to_id
- is_terminal
- is_lake ??
- is_headwater ??
- geom

### Model (id: model_id = identity_hash+domain_code)
- identity_hash
- domain_code (grid-snapped N/S/E/W offsets from the reach anchor, in CRS units)
- domain bbox geom

#### Identity (identity_hash = hash of this content)

Overrides are applied upstream and arrive folded into reach_geom / sources / params below; the `build_model` job itself doesn't take an override_id.

- sdr_commit (methodology version pin)
- reach_geom_hash
- dem_source_inputs_hash (ex usgs url + version)
- roughness_source_inputs_hash (ex nlcd url + version)
- lulc_lookup_dict_hash
- grid_resolution
- epsg_code

### Run (id: )
- scenario
- model_id
- execution time
- `runner` job version
- solver
- hotstart raster  (optional)
- STL (optional)
- KWSE transfer raster (optional)

#### Scenario (id:)
- q
- bc_type
- bc_value


## Storage Layout

Schemas:
model.json (model definition + artifact inventory; see build_model-design.md / model.schema.json)
metrics.parquet for qc analytics
run.json

```bash
s3://twod-fim/
└── version=v1/                             major repo/storage version only (minors coexist)
    ├── overrides/
    │   └── reach=12345/2026-05-01_levee-fix/{patch.tif, manifest.yaml}
    │
    ├── models/                             one physical build = one DEM clip
    │   └── reach=12345/
    │       └── model_id/   (= identity_hash+domain_code)   # group/rollback by identity_hash
    │              ├── model.json              input + output (written last)
    │              ├── metadata.csv / parquet  metadata on artifacts
    │              ├── {dem,roughness}.tif      derived; deletable after N days
    │              └── {cl,inflow,centroid,domain}.geojson
    │
    └── results/                            
        └── reach=12345/
            └── <identity>/  # runs file under identity, not under domain
                └──	<hash(run_identity)>/    # solver; group/rollback by this
                    └── z=283/f=200/      or .../z=nd/f=200/   # run realization: scenario point
                    	├── depth.tif           COG, EPSG:5070; also the hot-start seed
                    	├── stl.geojson           Stage Transfer Line
                    	├── metadata.csv / parquet  metadata on artifacts
                    	└── run.json            self-describing run record (records domain used)
```

## Repo Layout

![alt text](guide-diagrams/repos-and-ownership.drawio.png)

## Basic Sequence

![alt text](guide-diagrams/run-sequence.drawio.png)

## Open Questions

- How does worker wait for last scenario of downstream reach to finish?
  Possibly by waiting for `state_synced=true`
- Do we want more granular control over desired kwse state
- How do we track nominal KWSE rasters
- Does PSQL trigger orchestrator or orchestrator watches PSQL
- How do AWS Batch runs DIND
- Network traversal order
