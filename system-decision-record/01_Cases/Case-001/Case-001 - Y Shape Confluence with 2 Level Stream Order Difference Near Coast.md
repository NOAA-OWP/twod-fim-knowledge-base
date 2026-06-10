---
type: case
case_id: Case-001
title: Y Shape Confluence with 2 Level Stream Order Difference
date_observed: 2026-01-22
coordinates_5070: 1930357, 2289467
coordinates_4326: 41.466439,-72.470839
flows:
  - "500"
  - "6000"
tags:
  - case
  - confluence
  - stream-order
  - "#coastal"
  - "#flat"
stream_orders:
  - "4"
  - "6"
location: Haddam, CT
river_names:
  - Connecticut
  - Salmon
---


![[01_Cases/Case-001/FIG-001.png]]


## Description

- Confluence with stream-order mismatch appears sensitive to KWSE handling
- Reaches in flat areas are sensitive to backwater effect downstream reaches
- Y Shape provides a frequent network pattern

## Experiments
### 1. [[EXP-001 - KWSE Enforced FIM vs ND FIM]] on Reach 3463057

`Decision Register` at: `unknown`

The reach was modeled with two different boundary conditions at the `reach outlet`. 
1. A normal depth (ND) run, where water was allowed to leave the domain at normal depth slope.
2. A KWSE run where, known water surface elevation was inforced at `STL` 

The following image depicts the difference in water depth along the reach center line. The KWSE water depths are higher meaning that if KWSE from downstream model is not enforced for this reach, the reported depths from will be less than what they should be.  The difference is most visible at the `STL` (where KWSE is enforced) as expected. 

![[01_Cases/Case-001/FIG-002.png]]

This results provide basis for rejecting the idea that we can ignore KWSE model runs because this leads to [[ISU-001 - Lower WSEL towards the end of the Reach]].

> [!Error] Reject
> [[DR-001 - Should KWSE Scenario be Modeled or Not|DR-001 - Should KWSE Scenario be Modeled or Not?]] > [[DR-001 - Should KWSE Scenario be Modeled or Not#ALT-B - For No Reach|ALT-B - For No Reach]]

## 2. [[EXP-002 - Run a Model with All Edges at Normal Depth]]

`Decision Register` at: `unknown`

A combined 2D model was created for reach 3463058, 3463057, and 3463056 with domain hand drawn to what it should be for this area, this eliminated uncertainty about domain extent and allowed us to focus on edge boundary conditions.  When the model was executed with all edge cells at normal depth condition, the water was leaving the system at non outlet location [[ISU-003 - Water Leaving the Domain At Non Outlet Locations]].

![[01_Cases/Case-001/FIG-003.png]]

> [!Error] Reject
>[[DR-003 - Where and What Boundary Conditions to Apply Along the Edge Cells of a KWSE Run]] > [[DR-003 - Where and What Boundary Conditions to Apply Along the Edge Cells of a KWSE Run#ALT-A - Normal Depth at all Edges with Uniform Steep Slope|ALT-A - Normal Depth at all Edges with Uniform Steep Slope]]
