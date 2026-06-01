## Description
Each reach requires a minimum and maximum discharge to bound the simulation library. These bounds determine the range of flows represented in the FIM database. Bounds must be applicable at CONUS scale without manual intervention.

## Alternatives

### ALT-A - Fixed Recurrence Interval Bounds from NWM Retrospective
#current

Analyze National Water Model (NWM) retrospective flows to fit a flood frequency distribution (e.g., LP3) at each reach. Use the 5-year recurrence interval discharge as the lower bound and the 500-year recurrence interval discharge as the upper bound. This approach leverages existing national datasets, scales to all NHD reaches without manual tuning, and produces physically grounded bounds tied to flood frequency.

### ALT-B - User-Specified Fixed Discharge Bounds
Operators define a single pair of discharge values applied uniformly to all reaches. Simple to implement but ignores the orders-of-magnitude variation in channel capacity across CONUS. Results in unnecessary low-flow runs on large rivers and missing high-flow coverage on small streams.

### ALT-C - Channel Bankfull Discharge as Lower Bound
Use an estimated bankfull discharge as the minimum, below which floodplain inundation is negligible. Requires a reliable bankfull estimation method at every reach; current national datasets have high uncertainty for this quantity.

## Decision History
- 2026-06-01: ALT-A selected until a better option is proposed.
