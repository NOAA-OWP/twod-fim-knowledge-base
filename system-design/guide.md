## Guiding Requirements

- Run any single reach end-to-end on a developer laptop
- Mix and match minor updates
- Flexibility to add scenarios
- Flexibility to update model domain
- Flexibility to alternate between different solvers per reach

## Key Design Principles

- The System is designed with database as the brain plus pipeline as a reconciliation loop
- Pipeline has main goal of reconciling current state towards desired state
- Jobs are stateless, they intake JSON, output JSON. They write to S3
- Jobs do not interact with Database
- Pipeline is the sole writer/editor to deployed system, no external updates are allowed
- User updates come through override system
- Deployed system does not entertain testing, testing should be carried out separately and desired state must be updated via overrides or updates to desired state table
- Inputs are versioned
- Outputs are immutable and stored at addressed paths (A rerun with same inputs will overwrite the old content)
- If the desired state changed exiting outputs become stale and they are handled by S3 lifecycle policies
- Self documenting paths
- Operational Unit is per reach folder. Someone can `aws s3 sync` one reach to a laptop and have everything to inspect or rerun
- Stateless code i.e. function shaped, no load-mutate-save lifecycle
- What can be derived, will not be stored beyond some days on S3
- Desired state should be preserved at all cost as it will update as system would self update as well as updates from external users

## Key Design Decisions

- STL is not part of model definition, but STL will inform model_domain desired state
- Model = model_identity (reach + methodology + overrides) + realization (domain)
- Run = run_identity (engine + engine version) + realization (scenario: q, kwse)
- Identity and realization are always separate component in hashes and separate DB columns so that group / roll back / delete by either is possible
- Runs with same model_identity stay valid even if a domain change updates the model hash
- The database has three main tables
- Desired state = input to system = authored intent
- Current state = what's actually been achieved = current state of the system
- Runs = the per-run record (ledger)
- Rollback = revert desired state; content-addressing reuses prior outputs if not yet aged out, else will be recomputed

## Versioning Model

- When we store in S3 we store by repo version, (minor updates can live together, but major can not)
- Each version is pinned to a commit in SDR

## Key System Objects

### Model

#### Model Identity

#### Model Domain

### Scenario

### Run

## Storage Layout

Schemas:
model.manifest.json (where do you want to store metadata about your artifacts..)
metrics.parquet for qc analytics
run.manifes.json

```bash
s3://twod-fim/
└── version=v1/                             major repo/storage version only (minors coexist)
    ├── overrides/
    │   └── reach=12345/2026-05-01_levee-fix/{patch.tif, manifest.yaml}
    │
    ├── models/                             one physical build = one DEM clip
    │   └── reach=12345/
    │       └── <hash(model_identity)+<domain_geohash>/             # identity — group/rollback by this
    │              ├── manifest.json           input + output
    │              ├── metadata.csv / parquet  metadata on artifacts
    │              ├── {dem,roughness}.tif      derived; deletable after N days
    │              └── {centerline,inflow,outflow,domain,stl}.geojson
    │
    └── results/                            
        └── reach=12345/
            └── <hash(model_identity)>/  # runs file under identity, not under domain
                └──	<hash(run_identity)>/    # solver; group/rollback by this
                    └── z=283/f=200/      or .../z=nd/f=200/   # run realization: scenario point
                    	├── depth.tif           COG, EPSG:5070; also the hot-start seed
                    	├── stl.geojson           Stage Transfer Line
                    	├── metadata.csv / parquet  metadata on artifacts
                    	└── run.json            self-describing run record (records domain used)
```

## Open Questions

- How does worker wait for last scenario of downstream reach to finish?
    Possibly by waiting for `state_synced=true`
- Do we want more granular control over desired kwse state
- How do we track nominal KWSE rasters
- Does PSQL trigger Pipeline or Pipeline watches PSQL
- How do AWS Batch runs DIND