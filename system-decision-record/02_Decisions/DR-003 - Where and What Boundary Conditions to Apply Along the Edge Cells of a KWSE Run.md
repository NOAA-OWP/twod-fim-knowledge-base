## Description
Define which boundary condition should be applied along model edge cells (the domain bounding box). This is relevant during KWSE runs.  

Boundary Condition Choices Available:
1. Close / No Boundary Condition - Water pools at the edges
2. Normal Depth - Water escapes the domain at provided slope
3. Freefall - Water falling off of a cliff with no resistance

## Alternatives
### ALT-A - Freefall at all Edges
Water exits the domain at no resistance.

| Case | Outcome | Reason |
| --- | --- | --- |
| [[Case-001 - Y Shape Confluence with 2 Level Stream Order Difference Near Coast]] | #reject | [[ISU-003 - Water Leaving the Domain At Non Outlet Locations]] |

### ALT-B - Normal Depth at all Edges with Tailored Slope
This alternative applies normal-depth behavior to all edges but computes local slope values per edge cell, aiming to better model physical reality.

### ALT-C - D/S Model FIM Informed Edge Cells get Reach Centerline Slope
Apply reach centerline slope normal depth boundary condition only along edge cells identified as part of downstream reach FIM, leaving other edge segments closed.

![[DR-003 - FIG-001.png]]

### ALT-D - D/S Model FIM Informed Edge Cells get Freefall
#current

This is similar to ALT-A but only the edge cells that are intersecting with D/S reach FIM gets a freefall boundary condition. A freefall is needed because we want water to escape without resistance and not elevate WSEL in the `transition zone`. ALT-C suggestion of centerline slope with normal depth is a crude approximation of flow conditions, and is often based on a slope value with limited accuracy.  If the slope is flatter, it can lead to water being pooled in the transition zone. 

## Decision History
- Initially assumed started with Alt-A
- Switched to Alt-C
- 2026-02-16: Switched to ALT-D as ALT-C overlooked original need of freefall
