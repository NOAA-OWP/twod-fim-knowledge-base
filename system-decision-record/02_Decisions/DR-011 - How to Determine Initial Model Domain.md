## Description
The first step of model creation is determining the model extents. Some initial estimate of floodplain size must be made.
The decision on how to catch smaller domains and extend them is recorded in DR-012

## Alternatives
### ALT-A - Buffer on Reach Divide
In this approach, the bounding box of the reach divide and upstream boundary condition is buffered and used for the model domain.
### ALT-B - Buffer on Centerline
In this approach, the a bounding box is taken on some buffer around the stream centerline. The buffer distance could come from
 - a regression equation ([ex. Bieger et al., 2015](https://onlinelibrary.wiley.com/doi/abs/10.1111/jawr.12282)),
 -  an external dataset of river widths (ex. [from USGS](https://water.usgs.gov/catalog/datasets/120270a9-e0b6-42d8-9b1f-17db852fd2b4/)), or
 - a preliminary hydraulic calculation (ex. some assumption of channel depth combined with Manning's equation for a large flood).
### ALT-C - Coarse Model FIM
In this approach the assumption is that a course model would have been already executed for the reach, which will give a maximum FIM and the domain in actual modeling can simply be BBOX of the coarse model FIM

## Linked Cases Summary Table

| Alt | Case                                                                         | Link    | Reason                               |
| --- | ---------------------------------------------------------------------------- | ------- | ------------------------------------ |
| A   | [[01_Cases/Case-004 - Model Domain Example/Case-004 - Model Domain Example]] | #reject | Alt A led to a truncated floodplain. |


## Decision History
- 2026-02-2: Initial draft created
