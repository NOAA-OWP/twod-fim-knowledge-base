---
type: case
case_id: Case-004
title: Model Domain Example
date_observed: 2026-01-27
coords: (1798555, 2602987) [EPSG:5070]
flows:
  - "2344"
tags:
  - case
  - domain
stream_orders:
  - "4"
---
## Description

 - This case examines a situation where the approach of using the reach divide for the model domain led to FIM underestimation.

![[01_Cases/Case-004/FIG-001.png]]



## Experiments

### [[EXP-005 - Run a Model with Domain Developed from Reach Divide]] for reach 30728
Comparison to benchmark FIM from FEMA
![[01_Cases/Case-004/FIG-002.png]]

---
## Linked Decisions Summary Table

| Decision                                | Alternative                                                            | Outcome | Evidence                                    |
| --------------------------------------- | ---------------------------------------------------------------------- | ------- | ------------------------------------------- |
| [[DR-011 - How to Determine Initial Model Domain]] | [[DR-011 - How to Determine Initial Model Domain#ALT-A - Buffer on Reach Divide]] | #reject | [[ISU-006 - FIM cutting off arbitrarily at edges]] |


