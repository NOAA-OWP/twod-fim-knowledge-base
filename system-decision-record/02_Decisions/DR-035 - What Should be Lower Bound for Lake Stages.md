## Description
Lakes and coasts would be seeding points for Flows2FIM. The range of stage for these points would affect upstream network number of runs.

## Alternatives

### ALT-A - Lower Bound be Dead Pool Elevation
#current
Assumption is that we can get a dataset with dead pool polygon and corresponding stage available.

- Pro: better separation of concerns; lake extent is defined independently of DEM data.
- Con: extent and DEM may disagree, which can leave gaps in the FIM at the lake margin.

### ALT-B - Drive the Lake Polygon and Stage Directly from the DEM and Consider it the Floor Value
If we let the DEM define the pool, the lowest achievable surface is limited by the DEM (which usually represents the water surface at the time of DEM data collection, not the lake bottom / dead pool).

- Pro: no break/gap in FIM at the lake edge.
- Con: the floor is bounded by the DEM water surface, not the actual dead pool.

## Decision History
- 2026-05-28: Drafted from meeting notes; tradeoff captured, ALT-A tentatively favored.
