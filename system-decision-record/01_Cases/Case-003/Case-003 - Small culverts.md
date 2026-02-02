---
type: case
case_id: Case-003
title: Small Culverts
date_observed: 2026-01-27
coords: (1796329.9, 2607407.4) [EPSG:5070]
flows:
  - "36.75"
tags:
  - case
  - culverts
  - structures
stream_orders:
  - "1"
---
## Description

This case exhibits two distinct issues that may occur when culverts are not adequately breached: [[ISU-005 - Divergent flowpath]] and [[ISU-007 - Culvert blocking flow]]. 


![[01_Cases/Case-003/FIG-001.png]]

## Experiments

### [[EXP-004 - Run a model using current Decision Register methodology]] on reach 30704

#### Decision Register:   e043d37

Changes:
- Use known water surface elevation from downstream reach (30683) as downstream boundary condition.


In the upstream area, FIM from the 2D model differs from the 100-year FEMA maps.

2D Model

[[01_Cases/Case-003/FIG-002.png]]

FEMA 100-year floodplain (blue)
[[01_Cases/Case-003/FIG-001.png]]
![[FIG-009.png]]

Image of the model DEM in this area
[[01_Cases/Case-003/FIG-003.png]]

And a higher-resolution copy from the source USGS terrain
[[01_Cases/Case-003/FIG-004.png]]

Further downstream, culverts impound flows. In one case, they prevent water from entering the downstream end of the model.

[[FIG-005.png]]
[[FIG-006.png]]
[[FIG-007.png]]
[[FIG-008.png]]

---
## Linked Decisions Summary Table

| Decision                                                                          | Alternative                                                                                          | Outcome | Evidence                                                    |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------------- |
| [[DR-010 - How should DEM data be modified to enforce drainage through culverts]] | [[DR-010 - How should DEM data be modified to enforce drainage through culverts#ALT-A - Do nothing]] | #reject | [[ISU-005 - Divergent flowpath]] |


