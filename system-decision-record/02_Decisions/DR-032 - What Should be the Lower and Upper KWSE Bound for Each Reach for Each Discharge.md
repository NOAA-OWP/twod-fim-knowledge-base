## Description

[[DR-001 - Should KWSE Scenario be Modeled or Not]] establish which reaches should have KWSE scenarios at all

This DR establish what should be range of upper and lower bounds for KWSEs.

## Alternatives

### ALT-A - Same as D/S Reach Max and Min STL WSEL Floored by Reach's Normal Depth WSEL at STL
#current

For every reach's every discharge we model it with full range of D/S Reach U/S WSEL range, but we don't model any KWSE that is lower than the reach's normal depth WSEL at the STL.

Straightforward to implement, test, and explain. Eliminates the risk of omitting a physically important combination due to a flawed sampling model.


## Decision History
- 2026-06-01: ALT-A selected for simplicity and to reduce initial study effort and complexity.
