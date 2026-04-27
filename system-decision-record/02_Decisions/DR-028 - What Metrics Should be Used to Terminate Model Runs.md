## Description
Reach-based hydraulic models require different run durations before they hit quasi–steady-state conditions. Furthermore, there is no single universally accepted definition of “quasi–steady.” In practice, this state may be characterized in several ways, including (1) convergence of outflow to inflow, (2) negligible temporal changes in water surface elevation or depth, or (3) stabilization of other state variables within a defined tolerance. Because of this ambiguity, a metric is required to determine when a simulation has effectively reached quasi-steady conditions and can be terminated.

## Alternatives

### ALT-A - Mean Depth Change

The depth difference at each cell was taken between each raster timestep, and the values were averaged across the raster. 

(Interpretation: Are depths changing by a small amounts? Does not take into account river size/depth magnitude variability.)

### ALT-B - Normalized Mean Depth Change

The Mean Depth Change metric was divided by the mean depth across all wetted cells at each timestep.  (Interpretation: Are depths changing by a small amount relative to the reach mean depth? Attempts to account for river size/depth magnitude variability.)

### ALT-C - Relative Depth Change

The difference in Mean Depth Change metric between timesteps was divided by the Mean Depth Change at the previous timestep. (Interpretation: Is the Mean Depth Change metric converging/showing a flat slope?)

### ALT-D - Coefficient of Variation

The depth difference at each cell was taken between each raster timestep, and the standard deviation of values was taken across the raster. This value was then divided by the mean cell depth. (Interpretation: Are depth changes highly variable within the reach? Is one area of the reach very stable while another still has areas filling?)

### ALT-E - Volume Convergence
#current 

Change in volume across the reach between timesteps normalized by the inflow volume in that period. Interpretation: Is the discharge out equal to the discharge in? Is the reach actively filling or draining?



## Decision History
- 2026-04-27: First selection of ALT-E
