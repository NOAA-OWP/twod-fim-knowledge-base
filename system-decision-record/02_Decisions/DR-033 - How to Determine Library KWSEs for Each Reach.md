## Description
Per [[DR-031 - Should Downstream Stage be Uniform or Cell-Specific Along the STL]], downstream boundary conditions are drawn from completed downstream reach simulations. Per [[DR-032 - What Should be the Lower and Upper KWSE Bound for Each Reach for Each Discharge]] we will have a range for d/s KWSE to work with, but within that range multiple simulations will exist producing many KWSEs. Each such simulation is attributed a nominal water surface elevation.

This decision addresses how to select the library values of downstream KWSEs to use as KWSE set for the current reach, so that the resulting library spans a useful range of downstream conditions without a large number of runs.

A critical aspect of this methodology is determining a "reasonable" set of downstream conditions for each modeled discharge.  To that end, the supplementary analysis below was conducted.

### Supplementary Analysis: Joint Frequency of Adjacent Reach Flows

**Hypothesis:** For adjacent reaches with similar drainage areas, the range of physically plausible downstream conditions for any given upstream discharge is narrow. The full cross-product of discharges and downstream conditions therefore contains a large share of implausible combinations.

**Method:**
1. Download 40-year NWM retrospective data for pairs of adjacent reaches (labeled tributary and mainstem).
2. Fit an LP3 distribution to each reach's annual maxima series.
3. Normalize hourly retrospective flows to recurrence interval (RI) units.
4. Select hours when either reach exceeds the 2-year flood.
5. If one reach is above 2-yr RI and the other is not, clip the other to 2-yr RI.
6. Plot the correlation between the two normalized timeseries.
7. Compute the drainage area ratio for all adjacent reach pairs in NHD.

![[DR-033 - FIG-001.jpeg]]

**Results:**

- **Near 1:1 drainage area ratio:** The two normalized flow timeseries show a nearly perfect linear relationship. It is extremely unlikely that OWP would ever issue a forecast pairing, for example, a 2-yr downstream water level with a 100-yr upstream discharge. For reaches like these, maps need only link each upstream discharge to the downstream conditions for the same approximate recurrence interval—though the downstream reach may still carry multiple upstream elevations per discharge.
- **Intermediate drainage area ratio:** The relationship becomes progressively noisier, indicating that a meaningful range of downstream conditions is plausible for each upstream discharge. Maps covering a spread of downstream conditions per upstream discharge are useful here.
- **Extreme ratio (small tributary into large mainstem):** The scatter plot shows an L-shape, which is partially an artifact of the clipping step. In practice, the data would form two lobes in the first and third quadrants. Because the two rivers flood by different mechanisms, it is unlikely they will have large floods simultaneously. The appropriate library structure for the tributary is: all upstream discharges paired with a baseflow downstream boundary condition, plus a small set of additional backwater runs all at low upstream discharge.


The full cross-product contains many combinations that will never appear in a real forecast, but the share of implausible combinations is strongly dependent on drainage area ratio. A static rule that discards combinations based on RI mismatch would need to vary by drainage area ratio to be correct. A brute-force cross-product is the conservative choice; smarter sampling is possible but requires a lengthy investigation to create and validate a joint distribution model.

## Alternatives

### ALT-A - Evenly Spaced by Nominal Elevation Index
Sort downstream simulations by their nominal water surface elevation. Select *n* simulations at evenly spaced indexes along that sorted list. The value of *n* is an operator-controlled parameter that can be used to control cost. This alternative naturally scales to any river size: a large river with large range of downstream elevations and a small river with few both yield a representative spread. The nominal stage interval actually sampled can be recorded as a quality metric, and new simulations can be added if fidelity issues arise.

```python
ds_scenarios.sort(key=lambda x: x.median_elevation)
ds_interval = len(ds_scenarios) // ds_resolution
ds_space = ds_scenarios[::ds_interval]
```

### ALT-B - Snap to a Per-Reach Standard Stage Grid
#current

Each reach picks a stage increment `Δz` from the discrete menu `{0.25, 0.5, 1, 2}` m. The library grid for that reach is built by stepping up from the per-discharge lower bound (from [[DR-032 - What Should be the Lower and Upper KWSE Bound for Each Reach for Each Discharge]]) rounded up to nearest `Δz` in increments of `Δz`, until the upper bound.

Examples for d/s WSEL range `224 → 227.1`:
- `Δz = 0.25` → `224, 224.25, 224.5, …, 226.5, 226.75, 227`
- `Δz = 1` → `224, 225, 226, 227`
- `Δz = 2` → `224, 226, 228`

Each grid stage is bound to the downstream simulation whose nominal stage is nearest, provided it is within `Δz/2`; that run's WSE raster is imposed on the STL (see [[DR-031 - Should Downstream Stage be Uniform or Cell-Specific Along the STL]]). Targets with no downstream run inside `Δz/2` are skipped as gaps in the downstream reach's own sampling.

### ALT-C - Scenarios Selected Based on Joint Frequency Analysis

Build a joint recurrence-interval distribution describing the relationship between upstream discharge and downstream water surface elevation for each reach pair. For each pair, either construct an empirical distribution directly from retrospective data or fit a parametric distribution whose parameters are predicted as functions of drainage area ratio. Sample downstream scenarios with density proportional to probability, concentrating fidelity in high-probability regions while still covering the full physically possible domain.

The supplementary analysis shows that drainage area ratio strongly governs this joint distribution: near 1:1 ratios produce narrow relationships; intermediate ratios produce progressively noisier but still correlated distributions; extreme ratios produce L-shaped or multi-modal patterns reflecting different flood mechanisms. For large rivers with strongly correlated adjacent reaches, this approach would substantially reduce computational cost or concentrate sampling in physically likely conditions. However, constructing a reliable joint distribution at CONUS scale introduces significant complexity and additional failure modes. Validation across diverse reach geometries and climates is substantial.


## Decision History
- 2026-06-01: ALT-B selected based on assumed client preference
