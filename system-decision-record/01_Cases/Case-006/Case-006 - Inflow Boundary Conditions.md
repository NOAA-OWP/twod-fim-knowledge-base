---
type: case
case_id: Case-006
title: Inflow Boundary Conditions
date_observed: 2026-02-04
coords: (1903629, 2354784) [EPSG:5070]
flows:
  - "13500"
tags:
  - case
  - inflow
  - connecticut
stream_orders:
  - "6"
---
![[01_Cases/Case-006/FIG-001.png]]

## Description

- Reach 3463421 modeled
- Connecticut River at Springfield, MA
- Discharges developed from USGS 01172000

## Experiments

### [[EXP-006 - Run a Model with Various Inflow Boundary Conditions]] for reach 3463421

#### Decision Register: [12d9eb9](https://github.com/NGWPC/twod-fim-knowledge-base/commit/12d9eb96020e737ee64052d7e163c7c54278ee80)

Changes:
- None, other than experiment


Examining the experiment condition of using a single point at the `reach start`, clear water surface elevation artifacts can be seen at the inflow point.  In the image below, the blue area is the modeled 500-year floodplain, and the white lines show the corresponding 0.1 meter contour lines.

![[01_Cases/Case-006/FIG-002.png]]

The image below shows the depth raster for that same event.
![[FIG-005.jpeg]]

[[ISU-008 - Water-surface Elevation Anomalies]] - The "bullseye" pattern around the inflow point could lead to model instability and unreliable results.  Furthermore, these water surface elevation artifacts could be visible in the final FIMs.  Given these results, we reject [[DR-013 - What Should be Geometry and Location of Input  BC#ALT-D - At Point Some Distance Away on the `Upstream Mainstem Reach`|DR-013 ALT-D]] and [[DR-013 - What Should be Geometry and Location of Input  BC#ALT-E - A Point at the `Reach Start`|DR-013 ALT-E]].

Examining the experiment of using a 100-meter wide line 25% upstream along the `upstream mainstem`, Some water surface artifacts are present, but they are much less pronounced.  

![[01_Cases/Case-006/FIG-003.png]]

These are a mild case of [[ISU-008 - Water-surface Elevation Anomalies]]. In most cases these may not be problematic, however, if [[DR-004 - Strategy of Pixel Value Calculation For Composite Maps#ALT-D - Pixelwise Max]] is used, the anomaly could be visible in a final FIM.

Examining the experiment of using a 100-meter wide line at the `reach start`, Some water surface artifacts are present.

![[01_Cases/Case-006/FIG-004.png]]

The image below shows the depth raster for that same event.
![[FIG-006.jpeg]]

These are a mild case of [[ISU-008 - Water-surface Elevation Anomalies]]. In most cases these may not be problematic, however, if [[DR-004 - Strategy of Pixel Value Calculation For Composite Maps#ALT-D - Pixelwise Max]] is used, the anomaly could be visible in a final FIM.

Furthermore, in some areas (notably, steep terrain), the "warm up" area will be required to allow the floodplain to fully expand before the reach of interest.

---
## Linked Decisions Summary Table

| Decision | Alternative | Outcome | Evidence |
| --- | --- | --- | --- |
| [[DR-013 - What Should be Geometry and Location of Input  BC]] | [[DR-013 - What Should be Geometry and Location of Input  BC#ALT-D - At Point Some Distance Away on the `Upstream Mainstem Reach`\|ALT-D - At Point Some Distance Away on the `Upstream Mainstem Reach`]] | #reject | [[ISU-008 - Water-surface Elevation Anomalies]] |
| [[DR-013 - What Should be Geometry and Location of Input  BC]] | [[DR-013 - What Should be Geometry and Location of Input  BC#ALT-E - A Point at the `Reach Start`\|ALT-E - A Point at the `Reach Start`]] | #reject | [[ISU-008 - Water-surface Elevation Anomalies]] |
| | | | |



