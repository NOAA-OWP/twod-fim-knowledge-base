## Description

Large bridges are generally removed from USGS 3DEP data, but many smaller culverts remain as flow obstructions in the terrain.  
## Alternatives

### ALT-A - Do nothing
This alternative proposes using DEM data directly from USGS without modifying it at all. This approach is somewhat justified, since the functioning of each individual culvert cannot be guaranteed during a flood event. 

Despite its simplicity, this approach is not always the most conservative approach.  As shown in [[ISU-005 - Unburned Culverts Lead to Incorrect Flow Path]], unburned culverts can divert flows into divergent flowpaths, leading to underestimation of downstream flood inundation extents.

| Alt | Case                          | Link    | Reason                                                      |
| --- | ----------------------------- | ------- | ----------------------------------------------------------- |
| A   | [[Case-003 - Small culverts]] | #reject | [[ISU-005 - Unburned Culverts Lead to Incorrect Flow Path]] |

## Decision History
- 2026-02-2: Initial draft created
