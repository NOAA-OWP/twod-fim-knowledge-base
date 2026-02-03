## Description

Large bridges are generally removed from USGS 3DEP data, but many smaller culverts remain as flow obstructions in the terrain.  
## Alternatives

### ALT-A - Do nothing
This alternative proposes using DEM data directly from USGS without modifying it at all. This approach is somewhat justified, since the functioning of each individual culvert cannot be guaranteed during a flood event. 

Despite its simplicity, this approach is not always the most conservative approach.  As shown in [[ISU-005 - Divergent flowpath]], unburned culverts can divert flows into divergent flowpaths, leading to underestimation of downstream flood inundation extents.

### ALT-B - AGREEDEM

The AGREEDEM workflow could be applied here to burn trapezoidal channels into the area around stream centerlines and enforce drainage through culverts.
https://web.pdx.edu/~jduh/courses/geog493f09/Students/W8_AGREE_ScottParker.pdf

### ALT-C - Burn streams into DEM at roads

https://www.whiteboxgeo.com/manual/wbt_book/available_tools/hydrological_analysis.html?highlight=burnstreams#burnstreamsatroads
https://jblindsay.github.io/ghrg/pubs/2016_Lindsay_ESPL.pdf

### ALT-D - Breach flow obstructions

https://fema-ffrd.github.io/overflow/user-guide/terrain-conditioning/breach/

### ALT-E - Custom terrain modification

Custom code could be written to clip flowpath lines to some buffer around the road network.  A trapezoidal channel could then be imputed in the area around the intersection.

| Alt | Case                          | Link    | Reason                                                      |
| --- | ----------------------------- | ------- | ----------------------------------------------------------- |
| A   | [[Case-003 - Small culverts]] | #reject | [[ISU-005 - Divergent flowpath]] |

## Decision History
- 2026-02-2: Initial draft created
