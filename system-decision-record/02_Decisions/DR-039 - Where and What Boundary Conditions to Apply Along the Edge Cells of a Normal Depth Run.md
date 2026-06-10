## Description
Define which boundary condition should be applied along model edge cells (the domain bounding box). This DR is specific to Normal Depth runs.  For KWSE runs see [[DR-003 - Where and What Boundary Conditions to Apply Along the Edge Cells of a KWSE Run]]

Boundary Condition Choices Available:
1. Close / No Boundary Condition - Water pools at the edges
2. Normal Depth - Water escapes the domain at provided slope
3. Freefall - Water falling off of a cliff with no resistance

## Alternatives
### ALT-A - Reach Centerline Normal Depth Slope at all Edges
All edge cells have a normal depth boundary condition applied using the reach centerline slope value.

| Case | Outcome | Reason |
| --- | --- | --- |
| [[Case-001 - Y Shape Confluence with 2 Level Stream Order Difference Near Coast]] | #reject | [[ISU-003 - Water Leaving the Domain At Non Outlet Locations]] |

### ALT-B - Normal Depth at all Edges with Tailored Slope
This alternative applies normal-depth behavior to all edges but computes local slope values per edge cell, aiming to better model physical reality.

Implementing this in SFINCS would be technically challenging but possible.
### ALT-C - D/S Model FIM Informed Edge Cells get Reach Centerline Slope
Apply reach centerline slope normal depth boundary condition only along edge cells identified as part of downstream reach FIM, leaving other edge segments closed.

![[DR-003 - FIG-001.png]]

### ALT-D -  D/S Model FIM Informed Edge Cells get Downstream Reach Centerline Slope

Apply reach centerline slope normal depth boundary condition only along edge cells identified as part of downstream reach FIM, leaving other edge segments closed. Apply a slope value from the downstream reach's slope along the reach centerline.

### ALT-E - Bankfull Width Derived Edge Cells get Downstream Reach Centerline Slope

Apply a multiplier on the bankfull width estimate to approximate floodplain width at the downstream end of the reach.  Identify the intersection of the downstream reach centerline and the domain bounding box.  Apply outflow conditions at edge cells within a radius of 1/2 estimated floodplain width of intersection point. Those outflow cells get a normal depth condition with value from the downstream reach's slope along the centerline.  

Provide a metric after the run that summarizes wetted perimeter cells.  Check connectivity of all wetted outflow cells.  Report number of wetted cells connected to the outflow cells as well as number of unwetted outflow cells.

### ALT-F - ALT-D When Available and Fallback to ALT-E otherwise
#current 
When user specifies a downstream run, use ALT-D.  Otherwise, default to ALT-E.
## Decision History
- 2026-06-04: Selected ALT-F
