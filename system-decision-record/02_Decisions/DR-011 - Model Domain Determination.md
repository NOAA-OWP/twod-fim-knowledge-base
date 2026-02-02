## Description
The first step of model creation is determining the model extents. Some initial estimate of floodplain size must be made. Furthermore, features may be necessary to update the model domain later on based on simulation results.

## Alternatives
### ALT-A - Buffer on Reach Divide
In this approach, the bounding box of the reach divide and upstream boundary condition is buffered and used for the model domain.
### ALT-B - Buffer on Centerline
In this approach, the a bounding box is taken on some buffer around the stream centerline. The buffer distance could come from a regression equation, an external dataset of river widths, or a preliminary hydraulic calculation.
### ALT-C - Coarse Model
A coarse model may be quickly run to approximate flood extents for the largest expected flood.
## Linked Cases Summary Table

| Alt | Case                                                                         | Link    | Reason                                |
| --- | ---------------------------------------------------------------------------- | ------- | ------------------------------------- |
| A   | [[01_Cases/Case-004 - Model Domain Example/Case-004 - Model Domain Example]] | #Reject | Alt A led to a truncated floodplain.  |


## Decision History
- 2026-02-2: Initial draft created