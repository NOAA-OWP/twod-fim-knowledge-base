## Description
Define whether KWSE scenarios should be modeled for all reaches or only selected reaches.

This decision establishes whether downstream-stage-aware scenarios are always represented in the library rather than treated as optional special cases.

### From Literature
[https://www.fema.gov/sites/default/files/2020-02/Hydraulics_OneDimensionalAnalyses_Nov_2016.pdf](https://www.fema.gov/sites/default/files/2020-02/Hydraulics_OneDimensionalAnalyses_Nov_2016.pdf)  
_"Absent established downstream elevations or a control cross section, the Mapping Partner  
should compute starting water-surface elevations using normal depth calculations (or slope  
area) at a cross section sufficiently distant downstream from the downstream limit of study so as  
to render the effects of uncertainties in the starting water-surface elevation negligible."_


### Supplementary Analysis: Backwater Sensitivity from Ripple1D Rating Curves

**Hypothesis:** For some reaches, varying the downstream stage has no measurable effect on upstream water surface elevation for a given discharge. For those reaches, modeling multiple downstream conditions per discharge wastes compute.

**Theory:** In steep reaches, gravitational forces dominate over hydrostatic pressure forces (Froude number approaching 1). Under these conditions, flow at the upstream end cannot "feel" the downstream water surface elevation and is instead controlled by the upstream discharge alone.

**Method:** Using the Ripple1D rating curve database (collection `mip_17100103`, selected at random), plot the relationship of downstream depth to upstream depth for each discharge at every reach.

*Note: The colored lines in these plots do not extend to the left of the normal-depth run. This was a hard-coded criterion in the Ripple1D pipeline, not an emergent hydraulic property.*

![[DR-001 - FIG-001.png|697]]
![[DR-001 - FIG-002.png]]

![[DR-001 - FIG-003.png]]
**Results — Three behavioral regimes were identified:**

- **Case 1 (normal-depth controlled):** For each discharge, the downstream depth has no measurable effect on upstream depth. The rating curves are flat horizontal lines. Modeling more than one downstream condition per discharge provides no additional information about the upstream water surface profile.
- **Case 3 (backwater dominated):** Each discharge can produce a large range of upstream depths depending on downstream depth. At high downstream depths, discharge has almost no effect on upstream depth—the reach is essentially pond-backed. At lower downstream depths, discharge exerts some influence, but downstream depth remains the dominant control.
- **Case 2 (transitional):** Behavior lies between Cases 1 and 3, demonstrating that this is a continuum rather than a binary classification.

In high-gradient, normal-depth-controlled reaches, extensive downstream condition sampling is wasteful, and a single downstream condition per discharge is sufficient to characterize the upstream water surface profile. Conversely, in strongly backwater-influenced reaches, extensive discharge sampling is the wasteful dimension—downstream stage drives the outcome. The two analyses together suggest that an adaptive scenario selection strategy could substantially reduce total run counts. However, implementing that strategy requires a reliable method for classifying backwater sensitivity at every reach, which introduces significant additional complexity and research time.

## Alternatives
### ALT-A - For All Reaches
#current

Model KWSE scenarios for all reaches so downstream-stage sensitivity is represented consistently across the national library.

### ALT-B - For No Reach
This option reduces library size and modeling effort significantly, but it assumes downstream-stage variability can be ignored in all reaches.

| Case | Outcome | Reason |
| --- | --- | --- |
| [[Case-001 - Y Shape Confluence with 2 Level Stream Order Difference Near Coast]] | #reject | [[ISU-001 - Lower WSEL towards the end of the Reach]] |
### ALT-C - Suppress Downstream Variation Where Backwater is Negligible

Identify reaches where upstream water surface elevation is insensitive to downstream stage at a given discharge (i.e., normal-depth-controlled or near-critical flow). For those reaches, simulate only a single downstream condition per discharge. This could reduce library size substantially for high-gradient reaches. Identification could use static reach attributes (slope, Froude estimates) or response curves from an initial set of runs. Analysis of Ripple1D rating curve data confirms that this behavior exists and is reach-dependent, but the identification logic adds complexity. Defaulting to ALT-A; this alternative remains viable if targeted cost reduction is required.
## Decision History
- 2026-01-22: Initial decision based on Case-001 evidence
