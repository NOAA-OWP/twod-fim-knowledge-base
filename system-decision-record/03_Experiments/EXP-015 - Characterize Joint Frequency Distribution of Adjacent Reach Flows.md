## Description

The bounds and sampling density of downstream KWSE scenarios for a given upstream discharge depend on how correlated adjacent reach flows are. A systematic understanding of this joint frequency relationship at CONUS scale would allow the methodology in [[DR-032 - What Should be the Lower and Upper KWSE Bound for Each Reach for Each Discharge]] and [[DR-033 - How to Determine Library KWSEs for Each Reach]] to move beyond brute-force cross-products toward elegant bounds and sampling strategies that are physically informed.

This experiment codifies the supplementary analysis described in DR-033 into a reproducible, scalable analysis.

## Methodology

### 1. Reach Pair Assembly
1. Extract all adjacent reach pairs from the NWM v3.0 reach network.
2. Compute the drainage area ratio (tributary drainage area / mainstem drainage area) for each pair.
3. Bin reaches by every 0.1 drainage area ratio.
4. Within each bin, randomly sample 100 reach pairs. These will serve as the test reaches that are a representative sample of all reaches without needing the compute to process all reaches.

### 2. Retrospective Flow Data
1. Download 40-year NWM v3.0 retrospective streamflow for all selected reach pairs.
2. Extract annual maximum series (AMS) for each reach.
3. Fit an LP3 distribution to each reach's AMS to estimate per-reach flood frequency.
4. Normalize the hourly retrospective flows to recurrence interval (RI) units using the fitted LP3 CDF.

### 3. Joint Distribution Characterization
1. Select hours when either reach in a pair exceeds the 2-year RI flood.
2. Clip the non-exceedance reach to 2-yr RI.
3. Fit a 2D empirical CDF to each reach as well as the correlation of each pair of series.

### 4. Distribution Shape Classification
1. Review CDFs and attempt fitting various bivariate distributions and copulas.
2. Train a regression model to predict mean CDF or distribution parameters for each drainage area ratio bin.

Once completed, the fitted regression model can be applied to any reach pair. Given an upstream reach's normalized discharge (conditional value), the 5th and 95th percentile of downstream discharges can be selected from the marginal distribution.  The downstream reach's FIM library may then be subset to discharges within that percentile bound, and the min and max nominal WSE can be used for the reach of interest's min and max KWSE values ([[DR-032 - What Should be the Lower and Upper KWSE Bound for Each Reach for Each Discharge]]).  The standard approach of [[DR-033 - How to Determine Library KWSEs for Each Reach#ALT-B - Snap to a Per-Reach Standard Stage Grid]] may then be used to develop scenarios, or downstream KWSE values can be sampled directly from the marginal distribution [[DR-033 - How to Determine Library KWSEs for Each Reach#ALT-C - Scenarios Selected Based on Joint Frequency Analysis]].

## Notes

- The clipping step in the methodology (step 2 of section 3) is a simplification that creates the L-shape artifact noted in DR-033. A sensitivity analysis removing the clip and using a full bivariate sample is recommended as a secondary analysis.
- Climate region stratification is important because flood seasonality and co-occurrence patterns differ substantially between, e.g., snowmelt-dominated western basins and rainfall-dominated eastern basins.
