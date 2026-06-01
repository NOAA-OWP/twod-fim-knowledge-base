## Description

[[DR-001 - Should KWSE Scenario be Modeled or Not]] establish which reaches should have KWSE scenarios at all

This DR establish what should be range of upper and lower bounds for KWSEs.

Two analyses were perfomed to supplement this decision.

---

### Analysis 1 — Joint Frequency of Adjacent Reach Flows

**Hypothesis:** For adjacent reaches with similar drainage areas, the range of physically plausible downstream conditions for any given upstream discharge is narrow. The full cross-product of discharges and downstream conditions therefore contains a large share of implausible combinations.

**Method:**
1. Download 40-year NWM retrospective data for pairs of adjacent reaches (labeled tributary and mainstem).
2. Fit an LP3 distribution to each reach's annual maxima series.
3. Normalize hourly retrospective flows to recurrence interval (RI) units.
4. Select hours when either reach exceeds the 2-year flood.
5. If one reach is above 2-yr RI and the other is not, clip the other to 2-yr RI.
6. Plot the correlation between the two normalized timeseries.
7. Compute the drainage area ratio for all adjacent reach pairs in NHD.

![[DR-032 - FIG-001.jpeg]]

**Results:**

- **Near 1:1 drainage area ratio:** The two normalized flow timeseries show a nearly perfect linear relationship. It is extremely unlikely that OWP would ever issue a forecast pairing, for example, a 2-yr downstream water level with a 100-yr upstream discharge. For reaches like these, maps need only link each upstream discharge to the downstream conditions for the same approximate recurrence interval—though the downstream reach may still carry multiple upstream elevations per discharge.
- **Intermediate drainage area ratio:** The relationship becomes progressively noisier, indicating that a meaningful range of downstream conditions is plausible for each upstream discharge. Maps covering a spread of downstream conditions per upstream discharge are useful here.
- **Extreme ratio (small tributary into large mainstem):** The scatter plot shows an L-shape, which is partially an artifact of the clipping step. In practice, the data would form two lobes in the first and third quadrants. Because the two rivers flood by different mechanisms, it is unlikely they will have large floods simultaneously. The appropriate library structure for the tributary is: all upstream discharges paired with a baseflow downstream boundary condition, plus a small set of additional backwater runs all at low upstream discharge.


The full cross-product contains many combinations that will never appear in a real forecast, but the share of implausible combinations is strongly dependent on drainage area ratio. A static rule that discards combinations based on RI mismatch would need to vary by drainage area ratio to be correct. A brute-force cross-product is the conservative choice; smarter sampling is possible but requires a lengthy investigation to create and validate a joint distribution model.

---

### Analysis 2 — Backwater Sensitivity from Ripple1D Rating Curves

**Hypothesis:** For some reaches, varying the downstream stage has no measurable effect on upstream water surface elevation for a given discharge. For those reaches, modeling multiple downstream conditions per discharge wastes compute.

**Theory:** In steep reaches, gravitational forces dominate over hydrostatic pressure forces (Froude number approaching 1). Under these conditions, flow at the upstream end cannot "feel" the downstream water surface elevation and is instead controlled by the upstream discharge alone.

**Method:** Using the Ripple1D rating curve database (collection `mip_17100103`, selected at random), plot the relationship of downstream depth to upstream depth for each discharge at every reach.

*Note: The colored lines in these plots do not extend to the left of the normal-depth run. This was a hard-coded criterion in the Ripple1D pipeline, not an emergent hydraulic property.*

![[DR-032 - FIG-002.png|697]]
![[DR-032 - FIG-003.png]]

![[DR-032 - FIG-004.png]]
**Results — Three behavioral regimes were identified:**

- **Case 1 (normal-depth controlled):** For each discharge, the downstream depth has no measurable effect on upstream depth. The rating curves are flat horizontal lines. Modeling more than one downstream condition per discharge provides no additional information about the upstream water surface profile.
- **Case 3 (backwater dominated):** Each discharge can produce a large range of upstream depths depending on downstream depth. At high downstream depths, discharge has almost no effect on upstream depth—the reach is essentially pond-backed. At lower downstream depths, discharge exerts some influence, but downstream depth remains the dominant control.
- **Case 2 (transitional):** Behavior lies between Cases 1 and 3, demonstrating that this is a continuum rather than a binary classification.

In high-gradient, normal-depth-controlled reaches, extensive downstream condition sampling is wasteful, and a single downstream condition per discharge is sufficient to characterize the upstream water surface profile. Conversely, in strongly backwater-influenced reaches, extensive discharge sampling is the wasteful dimension—downstream stage drives the outcome. The two analyses together suggest that an adaptive scenario selection strategy could substantially reduce total run counts. However, implementing that strategy requires a reliable method for classifying backwater sensitivity at every reach, which introduces significant additional complexity and research time.

## Alternatives

### ALT-A - Same as D/S Reach Max and Min STL WSEL Floored by Reach's Normal Depth WSEL at STL
#current

For every reach's every discharge we model it with full range of D/S Reach U/S WSEL range, but we don't model any KWSE that is lower than the Reach's 

Straightforward to implement, test, and explain. . Eliminates the risk of omitting a physically important combination due to a flawed sampling model.

### ALT-B - Joint Probability Sampling
Model the joint recurrence-interval distribution of upstream discharge and downstream stage. Sample more densely in high-probability regions and sparsely in low-probability regions. For large rivers with strongly correlated adjacent reaches, this would substantially reduce run count or concentrate fidelity in physically likely conditions. However, constructing a reliable joint distribution at CONUS scale introduces significant complexity and additional failure modes. A brute-force cross-product is preferred for now.

### ALT-C - Suppress Downstream Variation Where Backwater is Negligible

This belongs in DR-001

Identify reaches where upstream water surface elevation is insensitive to downstream stage at a given discharge (i.e., normal-depth-controlled or near-critical flow). For those reaches, simulate only a single downstream condition per discharge. This could reduce library size substantially for high-gradient reaches. Identification could use static reach attributes (slope, Froude estimates) or response curves from an initial set of runs. Analysis of Ripple1D rating curve data confirms that this behavior exists and is reach-dependent, but the identification logic adds complexity. Defaulting to ALT-A; this alternative remains viable if targeted cost reduction is required.

## Decision History
- 2026-06-01: ALT-A selected for simplicity and to reduce initial study effort and complexity.
