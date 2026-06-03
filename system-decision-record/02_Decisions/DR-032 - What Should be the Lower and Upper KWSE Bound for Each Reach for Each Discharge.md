## Description

[[DR-001 - Should KWSE Scenario be Modeled or Not]] establish which reaches should have KWSE scenarios at all

This DR establish what should be range of upper and lower bounds for KWSEs.

## Alternatives

### ALT-A - Same as D/S Reach Max and Min STL WSEL Floored by Reach's Normal Depth WSEL at STL
#current

For every reach's every discharge we model it with full range of D/S Reach U/S WSEL range, but we don't model any KWSE that is lower than the reach's normal depth WSEL at the STL.

Straightforward to implement, test, and explain. Eliminates the risk of omitting a physically important combination due to a flawed sampling model.


### ALT-B - Bounds Derived from Joint Frequency Analysis

Build a joint recurrence-interval distribution describing the relationship between upstream discharge and downstream water surface elevation for each reach pair (see supplementary analysis in [[DR-033 - How to Determine Library KWSEs for Each Reach]]). For a given upstream discharge, use the joint distribution to define the physically plausible range of downstream conditions, setting the lower and higher bounds at a certain percentile of the marginal distribution of downstream KWSEs conditioned on a specific discharge.

The drainage area ratio strongly governs these bounds: near 1:1 ratios produce a narrow conditioned range (upper and lower bounds nearly coincide with the same-RI downstream stage); intermediate ratios produce a progressively wider range; extreme ratios (small tributary into large mainstem) produce bounds anchored near baseflow at the low end and the full mainstem flood range at the high end. This approach would tighten the simulation envelope for correlated reaches while preserving the full range for uncorrelated ones. However, constructing a reliable joint distribution at CONUS scale introduces significant complexity and additional failure modes. Validation across diverse reach geometries and climates would be substantial.


## Decision History
- 2026-06-01: ALT-A selected for simplicity and to reduce initial study effort and complexity.
