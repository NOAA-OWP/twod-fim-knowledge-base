# LISFLOOD-FP and SFINCS: 2D Hydraulic Model Technical Comparison

## Introduction

We reviewed LISFLOOD-FP and SFINCS as candidate 2D hydraulic solvers for automated, reach-based flood inundation mapping. As part of that review, we implemented automation code that constructs all required model input files for each solver from a common internal data model. This document compares how each model achieves the hydraulic functionality we need and how we control that behavior through input files, parameters, and boundary conditions.

---

## SFINCS

### Input Files

The table below lists every file we use to run a SFINCS model.

| File | Format | Description |
|---|---|---|
| `sfincs.inp` | ASCII key=value | Main configuration and parameter file |
| `sfincs.msk` | Binary (uint8) | Cell activity mask |
| `sfincs.ind` | Binary (uint32) | Active cell index map |
| `sfincs.dep` | Binary (float32) | Terrain elevations at active cells |
| `sfincs.man` | Binary (float32) | Manning's n at active cells |
| `sfincs.src` | ASCII | Inflow source point coordinates |
| `sfincs.dis` | ASCII | Inflow discharge time series |
| `sfincs.bnd` | ASCII | Water level boundary point coordinates |
| `sfincs.bzs` | ASCII | Water level time series for boundary points |
| `sfincs.bdr` | ASCII | Normal depth boundary condition definition |

### Input File Formats

SFINCS supports both ASCII and binary input formats for the spatial grid files (`sfincs.dep`, `sfincs.man`, `sfincs.msk`). Binary is activated by setting `inputformat = bin` in `sfincs.inp` and is strongly preferred for production use — ASCII files are significantly larger and slower to read.

In binary mode, each spatial file contains only the values at active cells (mask > 0), stored as a flat array in Fortran column-major index order as determined by `sfincs.ind`. We write all spatial inputs in binary. The writing routine was adapted from the HydroMT-SFINCS open-source toolkit (Deltares). The process is: read the source raster with rasterio, flip it vertically to reconcile raster row-ordering with SFINCS's expected orientation, transpose the 2D array, apply the mask to select active cells only, cast to the target dtype, and write with `ndarray.tofile()`. The index file is written using `numpy.ravel_multi_index` in Fortran order, prepended with the active cell count as a uint32.

NetCDF input format is supported from SFINCS v2024.01 and is a strong candidate for future adoption. NetCDF would enable self-describing, CF-compliant spatial inputs with embedded CRS metadata, eliminating the need for a separate index file and simplifying GIS integration of both inputs and outputs.

> **Note:** SFINCS NetCDF outputs are currently bugged — post-processing is required to convert model results to usable GeoTIFFs before any downstream analysis or delivery.

### `.inp` Parameters

The `.inp` file is the entry point for a SFINCS run. It registers all input file paths and controls grid geometry, CRS, and simulation timing. The table below covers every parameter we set and how we use it.

| Parameter | How we use it |
|---|---|
| `x0`, `y0` | Southwest corner of the grid in the model CRS, derived from the domain bounding box |
| `mmax`, `nmax` | Number of columns and rows in the grid |
| `dx`, `dy` | Grid resolution; we use a square grid so these are always equal |
| `epsg` | EPSG code of the model CRS |
| `rotation` | Grid rotation angle in degrees (clockwise from CRS axes); set to `0` — see Grid and Domain section |
| `latitude` | Set to `0` for all projected (Cartesian) CRSes, which is always the case in our setup |
| `crsgeo` | Set to `0` to confirm Cartesian projection |
| `tref` | Reference time; anchored to `20000101 000000` |
| `tstart` | Simulation start time; set equal to `tref` |
| `tstop` | Simulation end time; computed by adding `sim_time` seconds to the reference date |
| `dtout` | Output write interval in seconds (`run.save_interval`) |
| `inputformat` | Set to `bin`; instructs SFINCS to read spatial inputs as binary rather than ASCII |
| `depfile` | Path to `sfincs.dep` |
| `manningfile` | Path to `sfincs.man` |
| `mskfile` | Path to `sfincs.msk` |
| `indexfile` | Path to `sfincs.ind` |
| `srcfile` | Path to `sfincs.src` |
| `disfile` | Path to `sfincs.dis` |
| `bndfile` | Path to `sfincs.bnd` |
| `bzsfile` | Path to `sfincs.bzs` |
| `bdrfile` | Path to `sfincs.bdr` |

Omitting `bndfile` or `bzsfile` from the `.inp` when water level BCs are intended is a silent failure — SFINCS substitutes WSE = 0.0 at those cells without any error or warning, immediately pulling flow out of the domain.

### Grid and Domain

SFINCS uses a structured grid defined by its origin (`x0`, `y0`), resolution (`dx`, `dy`), and dimensions (`mmax`, `nmax`) specified in `sfincs.inp`. A notable feature is support for a rotated grid: the `rotation` parameter specifies a clockwise rotation angle in degrees relative to the CRS axes, allowing the grid to be aligned with the primary flow direction and reducing the active cell count. We currently set `rotation = 0`. SFINCS also supports quadtree refinement, which allows the grid to be locally refined in areas of interest (e.g., the channel) while remaining coarser elsewhere, improving both resolution and compute efficiency. We have not used quadtree refinement to date but it is a clear candidate for future performance optimization.

Rather than treating all cells uniformly, SFINCS uses a mask to classify every cell in the grid before the simulation begins. The mask (`sfincs.msk`) assigns each grid cell one of the following integer classes:

- **0** — Inactive. Outside the active domain; not computed.
- **1** — Active. Standard computational cell participating in the hydraulic solution.
- **2** — Water level boundary. A prescribed WSE is enforced at this cell; coordinates registered in `sfincs.bnd`, values in `sfincs.bzs`.
- **5** — Normal depth boundary. A normal depth outflow condition is applied; controlled by `sfincs.bdr`.

In our implementation, the mask is initialized to all-1 across the full rectangular grid — we do not currently deactivate any cells with mask=0. The mask=0 class exists and can be used to carve irregular active domains out of the rectangular extent, but all our domains are fully active rectangles. Boundary cells (mask=2 and mask=5) are overwritten from that all-1 baseline.

This mask-based classification differs fundamentally from LISFLOOD-FP's approach. In LISFLOOD, all cells in the raster domain are treated as active by default, and boundary conditions are applied by specifying the coordinates of point sources in the `.bci` file — boundaries are an overlay on top of a uniformly active grid. In SFINCS, the mask is the mechanism that both defines the active domain and assigns boundary roles to specific cells. Outflow boundary cells are carved out of the domain explicitly at the mask level.

The index file (`sfincs.ind`) is derived from the mask and lists the indices of all cells where mask > 0 in Fortran column-major order. This index is what allows binary spatial inputs to be stored as active-cell-only flat arrays rather than full grids.

### Terrain and Roughness

Terrain is provided in `sfincs.dep` and roughness in `sfincs.man`. Both are binary float32 files containing only the values at active cells (mask > 0), extracted from source rasters and written in the order defined by `sfincs.ind`. Source rasters are read with rasterio, flipped vertically to reconcile raster row-ordering with SFINCS's expected orientation, and then the active-cell values are extracted by transposing the array and applying the mask.

### Inflow Boundary Conditions

Inflow is controlled by `sfincs.src` (source point coordinates) and `sfincs.dis` (discharge time series). Discharge is assigned on a cell-by-cell basis — each cell that touches the inflow line geometry becomes a source point with its own entry in `sfincs.src` and its own discharge column in `sfincs.dis`. The total inflow is distributed across however many source cells the line intersects.

We use a time-varying but constant inflow: `sfincs.dis` contains two rows — one at t=0 and one at t=sim_time — with the same discharge values, producing a steady inflow for the duration of the run. Because SFINCS requires one full row of discharge values per timestep for truly time-varying inflow, a hydrograph-driven run would require one row per output interval for the entire simulation, which can produce very large `.dis` files for long runs or fine output intervals.

Discharge values written to `sfincs.dis` are in m³/s, computed by multiplying the per-unit-width flux value by the grid resolution. Internally, both models store inflow as per-unit-width flux (m²/s) in the boundary condition data model; SFINCS multiplies by resolution at write time while LISFLOOD-FP performs an equivalent internal conversion. A future cleanup should consolidate this so the conversion happens in one place.

### Outflow Boundary Conditions

SFINCS supports two outflow mechanisms relevant to our workflow: prescribed water level boundaries (mask=2) and normal depth boundaries (mask=5).

**Prescribed water level (mask=2):** Cells designated as water level boundaries are listed by coordinate in `sfincs.bnd`, with corresponding WSE time series in `sfincs.bzs`. We use these cells for stage transfer boundaries, where the downstream model's WSEL is enforced at the upstream model's outlet. Boundary coordinates can be specified at a coarser resolution than the grid — SFINCS uses IDW to interpolate prescribed values to individual boundary cells. The `.bzs` file uses the same two-row time-series format as `.dis` — identical values at t=0 and t=sim_time. SFINCS does not accept negative WSE values in `.bzs` and will silently substitute 0.0, so all values are clipped to 0.0 before writing.

**Normal depth (mask=5):** The normal depth BC is controlled by `sfincs.bdr`. This file defines an orientation line and a slope, from which SFINCS derives the downstream WSE dynamically at each timestep. The format per boundary is a single line:

```
xb yb xi yi slope d
```

`xb, yb` is a point near the downstream boundary edge. `xi, yi` is a reference point interior to the domain. `slope` is the water surface gradient. `d` is the along-channel distance between the two points. When `d` is negative (we use `-1`), SFINCS automatically computes the straight-line distance between `(xi, yi)` and `(xb, yb)`. When `d` is a positive value, it is taken as the manually specified along-channel distance — preferable when the channel meanders significantly and straight-line distance would underestimate the true flow path length.

At each timestep, SFINCS samples the WSE `zi` at the interior reference point (or ground elevation if dry), then computes the downstream boundary WSE as `zs = zi - d * slope`. This is a linear gradient approximation, not a Manning's-based computation. The orientation of the line matters: SFINCS uses the geometry to determine which interior cell to sample, so the line must point from upstream to downstream.

We do not have direct water surface slope observations, so we use reach slope from NHD hydrofabric attributes. When the model starts from a dry initial condition, `zi` equals the bed elevation at the reference cell. With a gentle slope and a long distance, this can yield a downstream boundary WSE above the channel bed, causing initial backflow into the domain. This is expected behavior — the model stabilizes once upstream inflow establishes a genuine water surface at the reference cell. Backflow severity is proportional to slope flatness and reference distance.

The coordinates written to `sfincs.bdr` are computed programmatically: `xb, yb` is the midpoint of the FREE boundary cells, and `xi, yi` is the centroid of the model domain bounding box. This is an approximation that will require attention at highly sinuous outlets.

### Build and Deployment

SFINCS is distributed as pre-built Docker images on DockerHub in both CPU and GPU-enabled variants. No local compilation is required. GPU acceleration has shown substantial runtime reductions even on small instances:

| Image | Size | Runtime (`aws g4dn.xlarge`) |
|---|---|---|
| CPU | 507 MB | ~383 s |
| GPU | 2.8 GB | ~28 s (~14×) |

The GPU image is cost-competitive with CPU alternatives for production use.

---

## LISFLOOD-FP

### Input Files

The table below lists every file required to run a LISFLOOD-FP model. Unlike SFINCS, all spatial inputs are referenced by path in the `.par` file and consumed directly in their native raster format — no separate index or binary conversion step is involved.

| File | Format | Description |
|---|---|---|
| `<run_id>.par` | ASCII key-value | Main parameter and configuration file |
| `<run_id>.bci` | ASCII | Boundary condition types and locations |
| `<DEMfile>` | ARC ASCII raster | Digital elevation model (terrain) |
| `<manningfile>` | ARC ASCII raster | Spatially distributed Manning's n |
| `<startfile>` | ARC ASCII raster | Optional hot-start water depth grid |

### Input File Formats

LISFLOOD-FP uses plain ASCII for all configuration and boundary condition files (`.par`, `.bci`, `.bdy`) and ARC ASCII grid format for all spatial inputs. There is no binary input mode for terrain and roughness. The text-based approach is straightforward to inspect and debug, but produces larger files than binary equivalents at scale.

NetCDF output is available in LISFLOOD-FP but was not evaluated in this project. It is worth investigating for future work where GIS integration and post-processing of model results are important.

### `.par` Parameters

LISFLOOD-FP supports several solver formulations — diffusive, inertial (acceleration), subgrid, and full shallow water (Roe). Initial testing found the `acceleration` (inertial) solver to be the fastest for our use case, though no formal benchmarking across solvers has been completed. The `.par` file selects the solver and controls all other aspects of model setup. The table below covers every parameter we set.

| Parameter | How we use it |
|---|---|
| `resroot` | Prefix for all output file names (e.g., `resroot.mass`, `resroot-0001.wd`) |
| `dirroot` | Output directory; created automatically if it does not exist |
| `DEMfile` | Path to the ARC ASCII terrain raster |
| `manningfile` | Path to the ARC ASCII roughness raster; takes precedence over scalar `fpfric` if both are specified |
| `bcifile` | Path to the boundary condition file |
| `saveint` | Spatial output write interval in seconds; LISFLOOD default 1000 s, we use 900 s |
| `massint` | Mass balance file write interval in seconds; LISFLOOD default 100 s, we use 15 s |
| `sim_time` | Total simulation duration in seconds; default 3600 s |
| `initial_tstep` | Starting (and maximum) time step in seconds for the adaptive solver; LISFLOOD default 10 s, we use 0.5 s |
| `acceleration` | Keyword flag (no value); activates the 2D inertial solver. Without it, LISFLOOD defaults to the adaptive diffusive solver |
| `cuda` | Keyword flag; enables GPU execution when a CUDA device is available |
| `elevoff` | Keyword flag; suppresses writing of water surface elevation output files (`.elev`), reducing I/O overhead |
| `startfile` | Path to an ARC ASCII water depth raster used to hot-start from a prior model state |

Several additional parameters in the manual are worth knowing for production use. `checkpoint` turns on periodic checkpointing at a user-specified interval in hours of wall time; the model automatically resumes from a `.chkpnt` file if found at startup, which is valuable for long cloud runs that may be interrupted. `depththresh` (default 0.001 m) controls the wet/dry threshold — the depth below which a cell is treated as dry; adjusting this can help with stability in very shallow or frequently wetting/drying areas. `theta` adds numerical diffusion to the inertial solver when set below 1.0 (default 1.0); lowering it can stabilize runs in steep or complex terrain at the cost of some accuracy. `cfl` controls the CFL stability coefficient used for adaptive time stepping (default 0.7). `maxdepthonly` forces the model to export only maximum depth results rather than all time steps, which can substantially reduce output volume for library-generation runs. `stagefile` specifies point locations at which LISFLOOD writes a time series of water surface elevations to a `.stage` file — useful for virtual gauge output or model validation against observed data without processing full raster outputs.

### Grid and Domain

LISFLOOD-FP reads grid geometry (origin, resolution, extent) directly from the ARC ASCII header of the `DEMfile`. No separate grid configuration is required in the `.par` file. The model operates on a rectilinear grid aligned to the coordinate axes; there is no support for a rotated grid.

All cells in the raster domain are treated as active by default. Boundary conditions are applied by specifying the coordinates of boundary segments or point sources in the `.bci` file — boundaries are an overlay on a uniformly active grid. This differs from SFINCS, where the mask file explicitly classifies each cell's role before the simulation starts.

### Terrain and Roughness

Terrain is provided as an ARC ASCII raster referenced by `DEMfile`. Manning's n is provided as a spatially distributed ARC ASCII raster referenced by `manningfile`. Both must have identical spatial extent and resolution; LISFLOOD-FP infers grid dimensions from `DEMfile` and expects `manningfile` to match. No binary conversion or active-cell extraction is performed — rasters are read directly in their native format.

### Inflow Boundary Conditions

LISFLOOD-FP inflow is specified in the `.bci` file. The format supports both edge-segment BCs identified by cardinal direction (`N`, `E`, `S`, `W`) and point sources identified by `P`. We use exclusively the `P` (point source) format for all BCs — inflow, stage transfer, and normal depth outflow — because it produces a cell-by-cell specification that directly parallels how SFINCS registers boundary cells. Using the `N`/`E`/`S`/`W` edge format was deliberately avoided to keep the two models' boundary condition logic consistent and interchangeable.

For each inflow point, the `.bci` line is: `P x y QFIX value`, where `value` is the discharge per unit width in m²/s. LISFLOOD-FP multiplies this by the cell width internally to produce a volumetric flux in m³/s per point. The total discharge is divided evenly across all points on the inflow line at setup time.

Time-varying inflow is available via `QVAR`, paired with a `.bdy` time series file. We do not use `QVAR` in the current implementation; all runs use `QFIX` for steady inflow.

### Outflow Boundary Conditions

Outflow is also specified in the `.bci` file using `P` point sources. The primary option for our use case is `FREE`, which applies a normal depth (uniform flow) boundary condition. `FREE` applies **only to edge cells** — it cannot be placed in the domain interior. It is **one-way**: water cannot re-enter through a `FREE` cell. For the 2D acceleration solver this is a floodplain outflow BC — LISFLOOD computes Manning's equation flux using local simulated water depth at each timestep. The friction slope can be parameterized per cardinal direction (`N`, `S`, `E`, `W`); a user-specified constant slope can optionally be appended (`FREE 0.0006`) to override the locally computed slope. Because the outflow is computed dynamically from actual simulated conditions rather than from a prescribed gradient anchored to a potentially dry reference cell, this approach generally avoids the warmup backflow issue seen with SFINCS's linear gradient approximation during dry-start conditions. A prescribed constant stage (`HFIX`) or time-varying stage (`HVAR`, paired with a `.bdy` file) can also be applied for stage transfer boundaries; we use `HFIX` for all stage transfer BCs, with the WSE value sampled from the downstream model's results.

### Build and Deployment

LISFLOOD-FP must be compiled from source. Our fork is maintained at [https://github.com/Dewberry/lisflood-fp](https://github.com/Dewberry/lisflood-fp) and includes any patches applied during this project. A Docker container wrapping the compiled binary is used for cloud execution. GPU acceleration is available for the acceleration, FV1, and DG2 solvers when compiled with CUDA support.

| Image | Size |
|---|---|
| CPU | 1.1 GB |
| GPU | 3.5 GB |

---

## Recommendation

Both SFINCS and LISFLOOD-FP are approved for use in the automated reach-based FIM pipeline and satisfy the core requirements for structured grid execution, GPU acceleration, Linux and container deployment, and the boundary condition types needed for inflow, stage transfer, and normal depth outflow. The two models are interchangeable within the automation framework, and either can be selected on a per-run basis.
