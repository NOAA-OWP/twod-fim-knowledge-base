## Description
Conventional LiDAR systems cannot measure bathymetric data below the water surface at time of flight. In some rivers and during some flight conditions, this section channel geometry can represent a significant proportion of channel conveyance. By not accounting for below-LiDAR bathymetry, depth predictions may be highly inaccurate.

A literature review of methods for bathymetry estimation is provided here: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2020WR028301

## Alternatives

### ALT-A - No handling
#current 

Apply no explicit bathymetry handling and rely on available topographic terrain, carrying resulting channel-conveyance uncertainty as a known limitation.

| Case | Outcome | Reason |
| --- | --- | --- |
| [[Case-015 - Large River]] | [#reject](app://obsidian.md/index.html#reject) | [[ISU-010 - Water-surface Elevations Higher than Benchmark FIM]] |
### ALT-B - Regression on bathymetric surveys
A team of researchers at Purdue has continued research in the vein of [this paper](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020WR029521). Their continued work uses surveyed bathymetric data from the USACE ehydro dataset to train a machine learning regressor that predicts bathymetric data at the reach scale.

While the study is currently only piloted for sites along the Ohio River, this analysis could be expanded to all areas of the US.  If accuracy is still acceptable, this approach could be used in pre-processing to add an estimate of channel bathymetry to model DEMs.

### ALT-C - Regression on LiDAR time-of-flight flow quantiles
USGS LiDAR has metadata to record the time of lidar flight. For a given LiDAR survey, the USGS gages in the survey area can be retrieved, and the flow-duration curve quantile for that day could be retrieved. A regression for flow-duration curve on drainage area could then be created within the survey area, and the mean flow quantile from all gages could be used to map a discharge to every reach.

Manning's equation could then be used to determine how much area below LiDAR would be needed to convey the predicted discharge at LiDAR flight time. A trapezoidal or rectangular channel shape could be assumed.

This approach was used by researchers at the University of Vermont.

Implementation notes: requires a curated DEM/LiDAR metadata data product (per-tile flight dates and a DEM snapshot tied to each survey), and a regression because gaged coverage is not universal across all reaches.

![[DR-021 - FIG-001.png]]

### ALT-D - FATHOM's Channel Solver

*requires commercial purchase of this product*

Fathom’s Channel Solver uses computational fluid dynamics to calculate how large a channel needs to be in order to convey a specified flow of water within its banks. The method calculates the appropriate cross sectional area for every point along the river network, solving for depth given that other variables such as width and slope can be observed. This calculation is necessary because the depth of rivers cannot be measured over very large areas using remote sensing techniques.

1. Capture observed width from satellite data and slope from DEM
![[DR-021 - FIG-002.png|515]]

2. Calculate depth needed to convey the specified flow
![[DR-021 - FIG-003.png|515]]
![[DR-021 - FIG-004.png|512]]

Research Paper: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2020WR028301

### ALT-E - Flow reduction based on baseflow (NWM or USGS)
#current

Use a baseflow estimate (e.g., NWM long-term baseflow, USGS baseflow separation, or a low-flow quantile such as Q90/Q95) as a proxy for the discharge present in the channel at LiDAR flight time, and back out the missing below-LiDAR area via Manning's equation analogously to ALT-C.

Unlike ALT-C, this does **not** use DEM/LiDAR time-of-flight metadata, so it cannot match the actual stage on the day of the survey. It is therefore a crude approximation — it will tend to be systematically wrong wherever the survey was flown well above or well below baseflow conditions — but it has the advantage of being applicable everywhere (no dependence on flight-date metadata or nearby gages) and of using nationally available datasets.

Could be deployed as a fallback where ALT-C inputs (flight date, nearby gages) are missing.

### ALT-G - Override with topobathymetric (TB) DEM where available

Variant of ALT-A. Default to no special handling, but where a topobathymetric DEM (e.g., NOAA Coastal TBDEM, USGS 3DHP TBDEM tiles, USACE channel surveys) is available, substitute or merge it into the working DEM so the channel bottom is directly represented and no estimation is needed.

## Decision History
- 2026-02-02: Retroactively document current approach (ALT-A)
- 2026-05-08: Alt-G - Selected after a team meeting
