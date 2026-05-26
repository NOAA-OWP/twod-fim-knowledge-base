---
title: Decision Register
---
# Decision Register

The Decision Register represents the current methodology. It lists the active decisions and their current selections.

Status meanings:
- Draft: Decision exists but no alternatives yet.
- Proposed: Alternatives are documented, but no alternative marked `#current`.
- Alternate Selected: A current selection exists and is considered valid.
- Needs-Review: A selection exists but evidence is unclear or conflicting.
- Superseded: Decision replaced by another DR.

| Decision | Current Alternative | Status | Last Update | Notes |
| --- | --- | --- | --- | --- |
| [[DR-001 - Should KWSE Scenario be Modeled or Not]] | [[DR-001 - Should KWSE Scenario be Modeled or Not#ALT-A - For All Reaches\|ALT-A - For All Reaches]] | Alternate Selected | 2026-01-22 | |
| [[DR-002 - What is the Definition of Benchmark FIM for Model Connectivity Testing]] | [[DR-002 - What is the Definition of Benchmark FIM for Model Connectivity Testing#ALT-A - Composite 2D Model with Same Input Data\|ALT-A - Composite 2D Model with Same Input Data]] | Alternate Selected | 2026-01-01 | |
| [[DR-003 - Where and What Boundary Conditions to Apply Along the Edge Cells]] | [[DR-003 - Where and What Boundary Conditions to Apply Along the Edge Cells#ALT-D - D/S Model FIM Informed Edge Cells get Freefall\|ALT-D - D/S Model FIM Informed Edge Cells get Freefall]] | Alternate Selected | 2026-02-16 | |
| [[DR-004 - Strategy of Pixel Value Calculation For Composite Maps]] | [[DR-004 - Strategy of Pixel Value Calculation For Composite Maps#ALT-D - Pixelwise Max\|ALT-D - Pixelwise Max]] | Alternate Selected | | |
| [[DR-005 - For Lake and Coastal Reaches What Downstream Boundary Conditions Should be Applied]] | [[DR-005 - For Lake and Coastal Reaches What Downstream Boundary Conditions Should be Applied#ALT-C - Both KWSE and Reach Normal Depth Slope\|ALT-C - Both KWSE and Reach Normal Depth Slope]] | Alternate Selected | 2026-01-27 | |
| [[DR-006 - For Lake and Coastal Reaches Where and What Boundary Conditions to Apply Along the Edge Cells]] | [[DR-006 - For Lake and Coastal Reaches Where and What Boundary Conditions to Apply Along the Edge Cells#ALT-E - D/S Water Body Informed Edge Cells get Steep Slope\|ALT-E - D/S Water Body Informed Edge Cells get Steep Slope]] | Alternate Selected | 2026-02-16 | |
| [[DR-007 - How to Mark Reaches as Lake and Coastal Reaches]] | | Draft | | |
| [[DR-008 - What Should be an STL for Lake and Coastal Reaches]] | [[DR-008 - What Should be an STL for Lake and Coastal Reaches#ALT-B - Intersection of Model Domain and Water Body Polygon Boundary\|ALT-B - Intersection of Model Domain and Water Body Polygon Boundary]] | Alternate Selected | | |
| [[DR-009 - Where to Apply Stage Transfer Condition]] | [[DR-009 - Where to Apply Stage Transfer Condition#ALT-B - At `Reach Outlet`\|ALT-B - At `Reach Outlet`]] | Alternate Selected | | |
| [[DR-010 - How should DEM data be modified to enforce drainage through culverts]] | [[DR-010 - How should DEM data be modified to enforce drainage through culverts#ALT-A - Do nothing\|ALT-A - Do nothing]] | Alternate Selected | 2026-02-02 | |
| [[DR-011 - How to Determine Initial Model Domain]] | [[DR-011 - How to Determine Initial Model Domain#ALT-D - Bounding Box of Inflow BC, d/s `STL`, and Buffered Centerline\|ALT-D - Bounding Box of Inflow BC, d/s `STL`, and Buffered Centerline]] | Alternate Selected | 2026-02-12 | |
| [[DR-012 - What Strategy to be used for Determining if Domain Should be Expanded]] | [[DR-012 - What Strategy to be used for Determining if Domain Should be Expanded#ALT-G - Informed by Water-Surface Elevation with Regression Expansion Limit\|ALT-G - Informed by Water-Surface Elevation with Regression Expansion Limit]] | Alternate Selected | 2026-02-09 | |
| [[DR-013 - What Should be Geometry and Location of Input  BC]] | [[DR-013 - What Should be Geometry and Location of Input  BC#ALT-A - At Perpendicular Line Some Distance Away on Highest Drainage Area `Upstream Reach`\|ALT-A - At Perpendicular Line Some Distance Away on Highest Drainage Area `Upstream Reach`]] | Alternate Selected | 2026-02-02 | |
| [[DR-014 - What Should be Geometry and Location of Input  BC for `Headwater Reaches`]] | [[DR-014 - What Should be Geometry and Location of Input  BC for `Headwater Reaches`#ALT-B - At Points Distributed Along the Reach\|ALT-B - At Points Distributed Along the Reach]] | Alternate Selected | 2026-02-02 | |
| [[DR-015 - What Line Width Should be Used for Inflow BC Line]] | [[DR-015 - What Line Width Should be Used for Inflow BC Line#ALT-A - 100m Wide\|ALT-A - 100m Wide]] | Alternate Selected | 2026-02-02 | |
| [[DR-016 - What Upstream Offset Distance Should be Used for Inflow BC Line Placement]] | [[DR-016 - What Upstream Offset Distance Should be Used for Inflow BC Line Placement#ALT-A - 0.25 of Upstream Reach Length\|ALT-A - 0.25 of Upstream Reach Length]] | Alternate Selected | 2026-02-02 | |
| [[DR-017 - What Horizontal Resolution DEM Should be Used for Modeling]] | [[DR-017 - What Horizontal Resolution DEM Should be Used for Modeling#ALT-A - 10 meters\|ALT-A - 10 meters]] | Alternate Selected | 2026-02-02 | |
| [[DR-018 - What Source DEM Should be Used for Modeling]] | [[DR-018 - What Source DEM Should be Used for Modeling#ALT-A - USGS 3DEP\|ALT-A - USGS 3DEP]] | Alternate Selected | 2026-02-02 | |
| [[DR-019 - What Source Surface Roughness Data Should be Used for Modeling]] | [[DR-019 - What Source Surface Roughness Data Should be Used for Modeling#ALT-A - National Land Cover Dataset converted to Manning's n\|ALT-A - National Land Cover Dataset converted to Manning's n]] | Alternate Selected | 2026-02-02 | |
| [[DR-020 - What Lookup Table Should be Used for Land Cover Classes to Manning's n Relationship]] | [[DR-020 - What Lookup Table Should be Used for Land Cover Classes to Manning's n Relationship#ALT-A - USACE Dictionary\|ALT-A - USACE Dictionary]] | Alternate Selected | 2026-02-02 | |
| [[DR-021 - How Should Below Water Topobathy be Accounted for]] | [[DR-021 - How Should Below Water Topobathy be Accounted for#ALT-A - No handling\|ALT-A - No handling]] | Alternate Selected | 2026-02-02 | |
| [[DR-022 - What Metrics Should be Used to Terminate Model Runs]] | [[DR-022 - What Metrics Should be Used to Terminate Model Runs#ALT-G - Volume Convergence (-)]] | Alternate Selected | 2026-05-08 | |
| [[DR-023 - How to Deal with Short Reaches]] | [[DR-023 - How to Deal with Short Reaches#ALT-B - Merge Continuous Reaches that have Negligible Drainage Area Difference Up to Some River Mile Length\|ALT-B - Merge Continuous Reaches that have Negligible Drainage Area Difference Up to Some River Mile Length]] | Alternate Selected | 2026-01-30 | |
| [[DR-024 - What Should be Thresholds for Merging Short Reaches]] | [[DR-024 - What Should be Thresholds for Merging Short Reaches#ALT-A - 5% Drainage Area Difference, Upto 3 miles, Stream Order 3 or up\|ALT-A - 5% Drainage Area Difference, Upto 3 miles, Stream Order 3 or up]] | Alternate Selected | 2026-02-09 | |
| [[DR-025 - What Should be the Geometry of STL]] | [[DR-025 - What Should be the Geometry of STL#ALT-B - WSEL Contour From D/S FIM\|ALT-B - WSEL Contour From D/S FIM]] | Alternate Selected | 2025-02-09 | |
| [[DR-026 - Should There be 1 STL per Reach or 1 STL per Reach per RUN]] | [[DR-026 - Should There be 1 STL per Reach or 1 STL per Reach per RUN#ALT-A - 1 STL Per Reach From Largest Model Run\|ALT-A - 1 STL Per Reach From Largest Model Run]] | Alternate Selected | 2026-02-09 | |
| [[DR-027 - How do Deal with Flat Reaches]] | [[DR-027 - How do Deal with Flat Reaches#ALT-A - Do Nothing\|ALT-A - Do Nothing]] | Alternate Selected | 2026-02-09 | |
| [[DR-028 - What Value Should be Used to Determine Volume Convergence]] | [[DR-028 - What Value Should be Used to Determine Volume Convergence#ALT-A - 1e-3\|ALT-A - 1e-3]] | Alternate Selected | 2026-04-27 | |
