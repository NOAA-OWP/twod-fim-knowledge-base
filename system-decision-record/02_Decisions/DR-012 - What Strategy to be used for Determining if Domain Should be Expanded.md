## Description
The initial domain from DR-011 may not be large enough.  This may lead to situations where water pools on domain edges and the FIM underestimates extent 

This DR explores strategies for dynamically determining after a simulation whether water is pooling on an edge in a way that impacts FIM extents negatively and hence FIM should be expanded.

## Alternatives

### ALT-A Informed by `Adjacent Reaches` FIM

The domain should be expanded until there are no flooding cells on the edges other than cells that are intersecting with
- the `downstream reaches` FIM
- the buffer (acting as proxy for FIM) on the `upstream reaches` and `common outlet reaches`  using same approach as [[DR-011 - How to Determine Initial Model Domain#ALT-B - Buffer on Centerline]].

### ALT-B - Informed by Elevation
#current

The domain should be expanded until there are no flooding cells on the edges other than cells that have elevation lower than the elevation at the  `outlet point` of the reach.


## Linked Cases Summary Table

| Alt | Case | Link | Reason |
| --- | ---- | ---- | ------ |
| | | | |

## Decision History
