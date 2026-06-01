## Description
Downstream boundary conditions will be applied along the `STL` and in some geographies can exert strong control on the hydraulic response of a reach. The representation chosen here directly impacts accuracy in the transition zone between adjacent reach maps and the ability of the 2D model to reproduce complex cross-sectional flow patterns.

## Alternatives

### ALT-A - Single Uniform Stage Across the STL
Apply one scalar water surface elevation across all cells on the STL. Analogous to a 1D stage boundary. Simple to implement, but flattens lateral gradients that exist in wide floodplains, low-gradient systems, and complex and split flow settings. Eliminates many of the accuracy gains from 2D modeling. The STL geometry (a WSE contour) partially mitigates spatial inconsistency, but cannot fully recover lost cross-sectional variability.

### ALT-B - Cell-by-Cell Stage Transfer from Downstream Reach Simulation
#current

Assign the water surface elevation at each STL cell from the corresponding raster output of the downstream reach's simulation for the matching scenario. Requires the downstream reach library to be completed before the upstream reach is processed.

This preserves the full lateral water surface profile across the STL, including floodplain lobes, secondary channels, and backwater pockets. Each downstream simulation is attributed a nominal water surface elevation to identify and sort scenarios. That nominal value is used by [[DR-033 - How to Determine Library KWSEs for Each Reach]] to select which downstream simulations to use as boundary conditions.

## Decision History
- 2026-06-01: ALT-B selected to preserve accurate hydraulics.
