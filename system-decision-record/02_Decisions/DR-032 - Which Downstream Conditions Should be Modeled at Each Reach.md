## Description
Per [[DR-031 - Should Downstream Stage be Uniform or Cell-Specific Along the STL]], downstream boundary conditions are drawn from completed downstream reach simulations. Each such simulation is attributed a nominal water surface elevation. This decision addresses how to select the subset of downstream simulations to use as boundary conditions for the current reach, so that the resulting library spans a useful range of downstream conditions without an unmanageable number of runs.

## Alternatives

### ALT-A - Evenly Spaced by Nominal Elevation Index
Sort downstream simulations by their nominal water surface elevation. Select *n* simulations at evenly spaced indexes along that sorted list. The value of *n* is an operator-controlled parameter that can be used to control cost. This alternative naturally scales to any river size: a large river with large range of downstream elevations and a small river with few both yield a representative spread. The nominal stage interval actually sampled can be recorded as a quality metric, and new simulations can be added if fidelity issues arise.

```python
ds_scenarios.sort(key=lambda x: x.median_elevation)
ds_interval = len(ds_scenarios) // ds_resolution
ds_space = ds_scenarios[::ds_interval]
```

### ALT-B - Fixed Delta Elevation Across All Reaches
Select downstream scenarios whose nominal elevations fall closest to a fixed stage increment (e.g., every 0.5 m). One stage increment applied uniformly across all CONUS reaches is a one-size-fits-none approach: too coarse for flat coastal plains and small rivers, too fine for mountainous canyons and large rivers. Requires a national calibration effort and will remain inaccurate across diverse geographies.

### ALT-C - Reach-Adaptive Delta Elevation Based on Stream Order or Drainage Area
#current
Estimate an appropriate stage increment for each reach using stream order or drainage area, then select scenarios matching that increment. This provides an easily-documented increment but requires a national regression or lookup analysis that will be inaccurate in edge-case geographies and require added investigation effort.

## Decision History
- 2026-06-01: ALT-C selected based on assumed client preference
