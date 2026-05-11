When we expand model it will become everything same but higher domain

Is one run.json or many

Is this good that we don't have database for pipeline tracking and tracking everything via S3?

How does worker wait for last scenario downstream reach?

what do you mean by invalidating at different places?

Indexer shouldn't be event based, just a simple scan? Some time based?
later can be event based


How to manage deletes? > there is no delete, just redo
Event based or conciler 


---

## Guiding Requirements:
- Run any single reach end-to-end on a developer laptop
- Mix and match minor updates
- Flexibility to add scenarios


## Key Design Principles
- One source of truth i.e. S3
- Index is a derived view of the S3
- Event based pipeline
- Inputs are versioned
- Outputs are immutable and stored at addressed paths
- A rerun with same inputs will overwrite the old content
- New and old run will exist together and S3 lifecycle policy will take care of deletion, while indexer would update itself to be the valid view of the system
- Hive partiniong or self documenting paths
- Operational Unit is per reach folder. Someone can `aws s3 sync` one reach to a laptop and have everything to inspect or rerun.
- Stateless code i.e. function shaped, no load-mutate-save lifecycle.
- What can be derived, will not be stored beyond some days on S3.
- 


Versioning Model
- When we store in S3 we store by repo version, (minor updates can live together, but major can not)
- each version is pinned to a commit in SDR
- 


Schemas:
model.manifest.json
run.manifes.json

```
s3://owp-fim/
└── version=v1/ # notice just major
    ├── overrides/
    │   └── reach=12345/
    │       └── 2026-05-01_levee-fix/
    │           ├── patch.tif
    │           └── manifest.yaml
    │
    ├── models/
    │     └── reach=12345/
    │       └── manifest_hash/ # v1.1
    │           ├── manifest.json
    │           ├── rasters/
    │           │   ├── dem.tif # deletes after 30 days
    │           │   └── roughness.tif # //
    │           └── vectors/...
    │       └── manifest_hash/ # 1.2
    │           ├── manifest.json
    │           ├── rasters/
    │           │   ├── dem.tif # deletes after 30 days
    │           │   └── roughness.tif # //
    │           └── vectors/...
    │
    └── results/
        └── reach=12345/
            └── model_manifest_hash/
                run_hash ??
                    └── q=Q100/
                        └── kwse=2.5/
                            ├── depth.tif # also a hotstart file
                            └── run.manifest.json
```

