## Description
Conventional LiDAR systems cannot measure bathymetric data below the water surface at time of flight. In some rivers and during some flight conditions, this section channel geometry can represent a significant proportion of channel conveyance. By not accounting for below-LiDAR bathymetry, depth predictions may be highly inaccurate.

A literature review of methods for bathymetry estimation is provided here: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2020WR028301

## Alternatives

### ALT-A - No handling
#current

### ALT-B - Regression on bathymetric surveys

A team of researchers at Purdue has continued research in the vein of [this paper](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020WR029521). Their continued work uses surveyed bathymetric data from the USACE ehydro dataset to train a machine learning regressor that predicts bathymetric data at the reach scale.

While the study is currently only piloted for sites along the Ohio River, this analysis could be expanded to all areas of the US.  If accuracy is still acceptable, this approach could be used in pre-processing to add an estimate of channel bathymetry to model DEMs.

### ALT-C - Regression on LiDAR time-of-flight flow quantiles

USGS LiDAR has metadata to record the time of lidar flight. For a given LiDAR survey, the USGS gages in the survey area can be retrieved, and the flow-duration curve quantile for that day could be retrieved. A regression for flow-duration curve on drainage area could then be created within the survey area, and the mean flow quantile from all gages could be used to map a discharge to every reach.

Manning's equation could then be used to determine how much area below LiDAR would be needed to convey the predicted discharge at LiDAR flight time. A trapezoidal or rectangular channel shape could be assumed.  

This approach was used by researchers at the University of Vermont.

![[DR-021 - FIG-001.png]]

## Linked Cases Summary Table

| Alt | Case | Link | Reason |
| --- | --- | --- | --- |
| | | | |

## Decision History
- 2026-02-02: Retroactively document current approach (ALT-A)