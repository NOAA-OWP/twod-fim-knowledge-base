#terminal-reaches
## Description
Define how the reach network is modified where it crosses lakes during the network modification phase. The goal is to stop modeling reach hydraulics inside a level pool while preserving inflow/outflow connectivity for the library + mosaic.

This decision depends on a lake extent dataset, see [[DR-034 - What Dataset Should be Used to Define Lakes]], and is related to how terminal reaches are classified.

## Alternatives

### ALT-A - Trim and Tag Reaches Against a Dead Pool Polygon
#current

Modify the network against a `dead pool polygon` dataset (see [[DR-034 - What Dataset Should be Used to Define Lakes]]):

1. **Remove lake reaches.** Reaches with ~100% of their length inside the dead pool polygon are considered `lake reaches`. We do not model their hydraulics, so they are removed from the network.
2. **Trim partial reaches.** A reach only partially inside the polygon is clipped at the polygon boundary during network modification, so the modeled portion ends/starts at the lake edge.
3. **Tag trimmed reaches.** Record why a reach was trimmed:
   - `lake_outlet = True` — reach exits the lake (lake is upstream of it).
   - `lake_inlet = True` — reach enters the lake (lake is downstream of it).
4. **Inflow BC for lake outlets.** A `lake_outlet` reach has no `upstream mainstem reach` to receive inflow on (its upstream is the lake), so the standard placement in [[DR-013 - What Should be Geometry and Location of Input  BC]] does not apply. Even placing input BC line at the start the reach is problematic because the start of a reach downstream of lake could be inside the lake in the DEM. Place the inflow BC line within the reach at an offset distance downstream of its start. See [[DR-016 - What Upstream Offset Distance Should be Used for Inflow BC Line Placement]] for offset; the lake-outlet offset rule may warrant its own DR.


### ALT-B - Keep Reaches, Flag Only
Leave geometry unmodified and only tag reaches as in/out of a lake, letting the modeling step decide what to do. Simpler network step, but pushes lake logic into modeling and leaves reach segments inside the pool that we do not intend to model.

## Open Questions
- Exact overlap threshold that defines a `lake reach` (the meeting used "~100% overlap"; Case-013 used >75% of length).
- Whether the lake-outlet inflow offset should be a distinct DR from [[DR-016 - What Upstream Offset Distance Should be Used for Inflow BC Line Placement]].

## Decision History
- 2026-05-28: Drafted from meeting notes; ALT-A selected by judgement.
