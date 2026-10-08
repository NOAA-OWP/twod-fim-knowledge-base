## Description
This framework attempts to report inundation extents for quasi-steady-state conditions. Hydrodynamic solvers like LISFLOOD-FP and SFINCS are fundamentally unsteady models, but steady-state solutions my be obtained as the long-time-limit of a dynamic simulation, or approximated using quasi-steady assumptions for efficiency and numerical stability. There is no single universally accepted definition of quasi–steady. This state may be characterized in several ways, including (1) convergence of outflow to inflow, (2) negligible temporal changes in water surface elevation or depth, or (3) stabilization of other state variables within a defined tolerance.

Reach-based hydraulic models require different simulation durations to reach quasi-steady conditions that depends on multiple factors like the size of the reach, the magnitude of flow, etc. For the purposes of this system; a quasi steady state is when executing model for a longer duration will not yield any significant increase in depth or extent of floodplain. To automate this, a metric is required to determine when a simulation has effectively reached quasi-steady conditions and can be terminated.

## Alternatives

### ALT-A Check Qin ~ Qout at Frequent Intervals
Determine quasi-steady behavior using repeated checks that inflow and outflow are approximately balanced over the simulation horizon.

### ALT-B - Mean Depth Change (m/s)

The depth difference at each cell was taken between each raster timestep and divided by the timestep (dt). These "delta" values were then averaged across the raster for each timestep.

$$
\displaystyle
\overline{\Delta D}(t) =
\frac{1}{n m}
\sum_{i=0}^{n}\sum_{j=0}^{m}
\frac{
d_{i,j,t} - d_{i,j,t-1}
}{
\Delta t
}
$$

(Interpretation: Are depths changing by a small amounts? Does not take into account river size/depth magnitude variability.)

### ALT-C - Normalized Mean Depth Change (1/s)

The Mean Depth Change metric was divided by the mean depth across all wetted cells at each timestep.

$$
\displaystyle
\overline{\Delta D}_{\text{norm}}(t) =
\frac{
\overline{\Delta D}(t)
}{
\overline{D}_{\text{wet}}(t)
}
$$

(Interpretation: Are depths changing by a small amount relative to the reach mean depth? Attempts to account for river size/depth magnitude variability.)

### ALT-D - Relative Mean Depth Change (-)

The difference in Mean Depth Change metric between timesteps was divided by the Mean Depth Change at the previous timestep.

$$
\displaystyle
R_{\Delta D}(t) =
\frac{
\overline{\Delta D}_t - \overline{\Delta D}_{t-1}
}{
\overline{\Delta D}_{t-1}
}
$$

(Interpretation: Is the Mean Depth Change metric converging/showing a flat slope?)

### ALT-E - Slope Mean Depth Change (m/s2)

The difference in Mean Depth Change metric between timesteps was divided by the timestep.

$$
\displaystyle
S_{\Delta D}(t) =
\frac{
\overline{\Delta D}_t - \overline{\Delta D}_{t-1}
}{
\Delta t
}
$$

(Interpretation: Is the Mean Depth Change metric converging/showing a flat slope?)

### ALT-F - Depth Change Coefficient of Variation (-)

The depth difference at each cell was taken between each raster timestep, and the standard deviation of values was taken across the raster. This value was then divided by the mean cell depth.

$$
\displaystyle
CV_{\Delta D}(t) =
\frac{
\sigma\left(|\Delta D|\right)_t
}{
\overline{\Delta D}_t
}
$$

(Interpretation: Are depth changes highly variable within the reach? Is one area of the reach very stable while another still has areas filling?)

### ALT-G - Volume Convergence (-)
#current

Change in volume across the reach between timesteps normalized by the inflow volume in that period.

$$
\displaystyle
VC(t) =
\frac{
\frac{V_t - V_{t-1}}{\Delta t}
}{
Q_{\text{in}}
}
$$

(Interpretation: Is the discharge out equal to the discharge in? Is the reach actively filling or draining?)

It's worth noting that LISFLOOD-FP provides functionality to terminate runs when steady state is reached using this condition. Oddly, this option is only available as a command line flag in newer versions of the software and cannot be controlled from the .par file.  Further complicating the matter, the function does not work in GPU mode (CPU mode only).

Reference in the LISFLOOD-FP user manual:

![[DR-022 - FIG-001.png|697]]

### ALT-H - Inundated Area Change (m2/s)

The area of cells with depth greater than 0 was compared between each timestep.

$$
\displaystyle
\frac{dA}{dt} =
\frac{
A_t - A_{t-1}
}{
\Delta t
}
$$

(Interpretation: Are new cells wetting?)

### ALT-I - Normalized Inundated Area Change (1/s)

The Inundated Area Change metric was divided by the inundated area at each timestep.

$$
\displaystyle
\left(\frac{dA}{dt}\right)_{\text{norm}} =
\frac{
\frac{A_t - A_{t-1}}{\Delta t}
}{
A_t
}
$$

(Interpretation: Are new cells wetting? Normalized for reaches and rivers of different sizes.)

### ALT-J - Slope Volume Convergence (-)
#current

Change in volume convergence between timesteps divided by the timestep.

$$
\displaystyle
\Delta{VC}(t) =
\frac{
VC(t) - VC(t-1)
}{
\Delta t
}
$$

(Interpretation: Is volume convergence line flat?)

## Decision History
- Started with ALT-A
- Rejected ALT-A because Qout is not calculated when running LISFLOOD-FP in GPU mode
- 2026-04-27:  Selected ALT-G
