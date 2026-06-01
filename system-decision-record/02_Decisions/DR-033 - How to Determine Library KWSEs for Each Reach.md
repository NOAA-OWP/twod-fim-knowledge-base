## Description
Per [[DR-031 - Should Downstream Stage be Uniform or Cell-Specific Along the STL]], downstream boundary conditions are drawn from completed downstream reach simulations. Per [[DR-032 - What Should be the Lower and Upper KWSE Bound for Each Reach for Each Discharge]] we will have a range of for d/s KWSE to work with, but within that range multiple simulations will exist producing many KWSEs. Each such simulation is attributed a nominal water surface elevation. 

This decision addresses how to select the library values of downstream KWSEs to use as KWSE set for the current reach, so that the resulting library spans a useful range of downstream conditions without a large number of runs.

## Alternatives

### ALT-A - Evenly Spaced by Nominal Elevation Index
Sort downstream simulations by their nominal water surface elevation. Select *n* simulations at evenly spaced indexes along that sorted list. The value of *n* is an operator-controlled parameter that can be used to control cost. This alternative naturally scales to any river size: a large river with large range of downstream elevations and a small river with few both yield a representative spread. The nominal stage interval actually sampled can be recorded as a quality metric, and new simulations can be added if fidelity issues arise.

```python
ds_scenarios.sort(key=lambda x: x.median_elevation)
ds_interval = len(ds_scenarios) // ds_resolution
ds_space = ds_scenarios[::ds_interval]
```

### ALT-B - Delta Value Rounded to Nearest Value
#current

### ALT-C - Reach-Adaptive Delta Elevation Based on Stream Order or Drainage Area

*I think this is under developed alternative, an alternate here could be same as adaptive step for Q*

Estimate an appropriate stage increment for each reach using stream order or drainage area, then select scenarios matching that increment. This provides an easily-documented increment but requires a national regression or lookup analysis that will be inaccurate in edge-case geographies and require added investigation effort.

## Decision History
- 2026-06-01: ALT-B selected based on assumed client preference
