## Description
Each reach requires a minimum and maximum discharge to bound the simulation library. These bounds determine the range of flows represented in the FIM database. Bounds must be applicable at CONUS scale without manual intervention.

## Alternatives

### ALT-A - Fixed Recurrence Interval Bounds from NWM Retrospective
#current

Analyze National Water Model (NWM) retrospective flows to fit a flood frequency distribution (e.g., LP3) at each reach. Use the 0.9 x `high flow threshold` discharge as the lower bound and the 1.5 x 100-year recurrence interval discharge as the upper bound. This approach leverages existing national datasets, scales to all NHD reaches without manual tuning, and produces physically grounded bounds tied to flood frequency. This approach is exactly same as what was used to produce Ripple1D libraries.

### ALT-C - Channel Bankfull Discharge as Lower Bound with 500 year Discharge as Upper Bound
Use an estimated bankfull discharge as the minimum, below which floodplain inundation is negligible. Requires a reliable bankfull estimation method at every reach; current national datasets have high uncertainty for this quantity.

## Decision History
- 2026-06-01: ALT-A selected until a better option is proposed.
