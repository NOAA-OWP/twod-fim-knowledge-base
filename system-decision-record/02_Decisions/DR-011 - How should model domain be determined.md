## Description
The first step of model creation is determining the model extents. Some initial estimate of floodplain size must be made. Furthermore, features may be necessary to update the model domain later on based on simulation results.

## Alternatives
### ALT-A - Buffer on Reach Divide
In this approach, the bounding box of the reach divide and upstream boundary condition is buffered and used for the model domain.
### ALT-B - Buffer on Centerline
In this approach, the a bounding box is taken on some buffer around the stream centerline. The buffer distance could come from
 - a regression equation ([ex. Bieger et al., 2015](https://onlinelibrary.wiley.com/doi/abs/10.1111/jawr.12282)),
 -  an external dataset of river widths (ex. [from USGS](https://water.usgs.gov/catalog/datasets/120270a9-e0b6-42d8-9b1f-17db852fd2b4/)), or
 - a preliminary hydraulic calculation (ex. some assumption of channel depth combined with Manning's equation for a large flood).
### ALT-C - Coarse Model (w/ downstream dependency)
A coarse model may be quickly run to approximate flood extents for the largest expected flood.

An initial model could be developed using ALT-B.  Then a large flood could be run through the model.  Water would be allowed to pool up along edges covered by
 - the downstream model FIM or
 - the ALT-B buffer on the upstream reach.
 When water pooled on other edges, the model domain would be expanded, and the model would be rerun.  Once the coarse model completed running, the bounding box of the inundated area would be taken for the final model domain.

### ALT-D - Coarse Model (w/o downstream dependency)
A coarse model may be quickly run to approximate flood extents for the largest expected flood.

An initial model could be developed using ALT-B.  Then a large flood could be run through the model.  Water would be allowed to pool up along edges either
 - Lower than the WSE at the most downstream point of the flowpath or
 - Higher than the WSE at the most upstream point of the flowpath
 When water pooled on other edges, the model domain would be expanded, and the model would be rerun.  Once the coarse model completed running, the bounding box of the inundated area would be taken for the final model domain.

## Linked Cases Summary Table

| Alt | Case                                                                         | Link    | Reason                                |
| --- | ---------------------------------------------------------------------------- | ------- | ------------------------------------- |
| A   | [[01_Cases/Case-004 - Model Domain Example/Case-004 - Model Domain Example]] | #Reject | Alt A led to a truncated floodplain.  |


## Decision History
- 2026-02-2: Initial draft created
