# build_model

## Overview

Initialize a model for a single reach by generating the terrain, roughness, geometry, and boundary-condition artifacts required by downstream workflow steps.

## Inputs

### Required

| Name             | Type | Description                                                                     |
| ---------------- | ---- | ------------------------------------------------------------------------------- |
| reach_id         | int  | Reach identifier                                                                |
| db_uri           | str  | Connection information for external database to query reach geom and parameters |
| base_output_path | str  | Model output location                                                           |

### Optional

| Name                      | Type      | Description                                                                        |
| ------------------------- | --------- | ---------------------------------------------------------------------------------- |
| dem_source                | str       | DEM data source (may need to add more info later)                                  |
| roughness_source          | str       | Land cover data source (may need to add more info later)                           |
| other_geometries          | list[str] | text representations of geometries that must be included in the reach bounding box |
| domain_buffer             | float     | Domain buffer distance applied to bounding box generated from all geometries       |
| grid_resolution           | int       | resolution to resample DEM and roughness to                                        |
| walk_us_dist_pct          | float     | Upstream search distance parameter                                                 |
| epsg_code                 | int       | Output coordinate reference system                                                 |
| bankfull_width_multiplier | float     | Multiplier applied to estimated bankfull width                                     |
| lulc_lookup               | dict      | Mapping from land cover classes to roughness values                                |

## Processing Scope

- Retrieve reach and upstream reach geometries from the hydrofabric.
- Estimate bankfull width.
- Generate inflow geometry.
- Define the model domain.
- Acquire and clip DEM and land cover data.
- Convert land cover data to roughness values.
- Generate model metadata.
- Write model artifacts to storage.

## Artifacts

| Artifact                                   | Description                             |
| ------------------------------------------ | --------------------------------------- |
| base_output_path/model_id/dem.tif          | Terrain raster                          |
| base_output_path/model_id/roughness.tif    | Roughness raster                        |
| base_output_path/model_id/cl.geojson       | Stream centerline geometry              |
| base_output_path/model_id/anchor.geojson   | Domain anchor point / created from reach geom |
| base_output_path/model_id/domain.geojson   | Reach bounding box                      |
| base_output_path/model_id/model.json       | Model definition and artifact inventory |

`model.json` is an internal JSON record, **written last**. It records: inputs verbatim, `identity_hash` + `id`, the `identity` object that is hashed, the `domain` (bbox/anchor/offsets), `properties` (grid + computed + hydrofabric attrs), each asset's `href` / `source_url` / `checksum`, and any warnings. Schema is provided at: `model.schema.json`.

## Response

- identity_hash - str - see guide.md
- model_id - str - identity_hash + domain code 

`model_id = <identity_hash>+<domain_code>` is the folder name. The domain code encodes the domain rectangle as grid-snapped offsets, in CRS units, from the grid-snapped reach centroid (the anchor) to each edge: `N{n}S{s}E{e}W{w}` (fixed order, no separators), e.g. `N200S200E300W200`. Because `epsg_code` and `grid_resolution` are part of identity and offsets are grid-snapped, the code is the unique canonical name of the domain — no separate domain hash needed.

## Hashing

All hashes use **SHA-256** algorithm, lowercase hex, truncated to a fixed length per role. Identity hashes are **8 hex** (32-bit, scoped under `reach_id`); file checksums are **16 hex** (64-bit). Each hash is over a **canonical** preimage (canonical JSON = sorted keys, no insignificant whitespace), so the same content always hashes the same:

| Field                          | Length | Preimage                                       |
| ------------------------------ | ------ | ---------------------------------------------- |
| `identity_hash`                | 8      | canonical JSON of the `identity` object        |
| `reach_geom_hash`              | 8      | canonical WKB of the reach geometry            |
| `dem_source_inputs_hash`       | 8      | canonical DEM source params (name, version, …) |
| `roughness_source_inputs_hash` | 8      | canonical land-cover source params             |
| `lulc_lookup_dict_hash`        | 8      | canonical JSON of the `lulc_lookup` dict       |
| asset `checksum`               | 16     | the raw output file bytes                      |

## Out of Scope

- Model expansion.
- Scenario generation.
- Solver input generation.
- Hydraulic simulation.
- Post-processing.
- Anything with STLs

## Dependencies

- Python
- GDAL
- AWS CLI

## Errors

- Source raster datasets are unavailable - raises DatasetUnavailableError
- Raster processing fails - raises RasterProcessingError
- Output artifacts cannot be written - raises WriteFailureError
- Drainage area missing or invalid in reach db - raises InvalidAttributeError

## Checks

- check if model exists at output path - return immediately with warning that model already exists
- checks if inflow line only crosses reach at one point - if multiple crosses, complete job as normal and return warning
- check if model domain is large - if large, return warning
- check if all roughness values are similar - if very similar, return warning

## Performance

- Typical runtime: ~10 seconds per reach.

Given the short execution time, AWS batch overhead would drastically increase cost.  Run this locally instead.