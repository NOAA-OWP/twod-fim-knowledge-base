---
type: case
case_id: Case-018
title: Simple Mid-Sized Rural River
date_observed: 2026-04-01
coordinates_5070: 1809257,2600659
coordinates_4326: 44.413821,-72.997044
flows:
  - "1470"
  - "1400"
  - "1345"
  - "70"
  - "55"
tags:
  - case
  - demo
  - mid-sized
  - simple
  - composite
stream_orders:
  - "4"
location: Richmond, VT
river_names: Winooski River
---
![[01_Cases/Case-018/FIG-001.png]]
The image above shows the Winooski River in a rural area near Richmond, VT.
## Description

This site was chosen as the location for an initial demo of 2D methodology for OWP.  This site was selected because it is a relatively simple fluvial setting that did not present any edge cases under the methodology at the time.  In addition to demonstrating the current 2D methodology, [[EXP-013 - Compare Merged Results From Individual Models to a Single Model for a Large Area]] was conducted to assess the validity of the assumption that reach-based modeling yields comparable results to larger-domain models.

## Experiments

### [[EXP-013 - Compare Merged Results From Individual Models to a Single Model for a Large Area]]

**Decision Register at: cd3e6b0**

Changes:
 - Manual expansion of domain for reach 30913
 - Downstream outlet line manually defined using valley walls.

![[FIG-002.jpeg]]

The image above shows the reaches selected for this experiment. Discharges were developed for these reaches using a regional regression equation and are shown in the table below.

| Reach | DA | slope | Q100 |
| --- | --- | --- | --- |
| 30831 | 2504 | 0.000486 | 1470 |
| 30869 | 2451 | 0.000682 | 1400 |
| 30912 | 2423 | 0.003801 | 1345 |
| 30868 | 23 | 0.037797 | 70 |
| 30913 | 15 | 0.041875 | 55 |
The Depth FIM for each reach is shown below.
![[01_Cases/Case-018/FIG-003.jpeg]]
![[01_Cases/Case-018/FIG-004.jpeg]]
![[01_Cases/Case-018/FIG-005.jpeg]]

![[01_Cases/Case-018/FIG-006.jpeg]]
![[FIG-007.jpeg]]

The single model geometry for this area is shown below.
![[FIG-008.jpeg]]
The single model depth FIM is shown below.
![[FIG-009.jpeg]]Comparing the two depth FIMS yielded this raster of residuals.
![[FIG-010.jpeg]]![[FIG-011.png]]![[FIG-012.png]]
The models agreed extremely well. More than 90% of inundated cells disagreed less than 0.05 meters. This experiment indicated that the assumption that reach-based models merged with a pixelwise max function behave similarly to a single model approach is reasonable.

In conducting this experiment, irregularities were found in the depth residual raster.  The image below shows a zoomed in depth difference raster with the symbology bounded on -0.05 (red; reach-based higher) to 0.05 (blue; single model higher).

![[FIG-013.png]]

It was determined that these differences were due to DEM differences as opposed to hydraulic model result differences. This is a case of [[ISU-011 - DEM Differences]]. The root cause of this issue may be the .vrt query itself or one of the transform operations within the modeling pipeline.  Further investigation is needed.

To arrive at a reasonable comparison, a difference map for water surface elevation was generated. This effectively circumvents the DEM differences.  While reviewing these results, some artifacts from reach-based model domains were found.  They can be seen in the image below. Symbology bounded on -0.05 (red; reach-based higher) to 0.05 (blue; single model higher).

![[FIG-014.png]]
This is a case of [[ISU-008 - Water-surface Elevation Anomalies]].  The inflow boundary conditions create elevated water surfaces in their vicinity.  When using the [[DR-004 - Strategy of Pixel Value Calculation For Composite Maps#ALT-D - Pixelwise Max]] approach is flawed.  Given that these differences are generally less than 0.05 meters, we choose not to reject ALT-D.


### [[EXP-014 - Compare Automated Steady State Determination to Modeler Determination]]

**Decision Register at:   cd3e6b0**

Changes:
 - Manual expansion of domain for reach 30913
 - Downstream outlet line manually defined using valley walls.

Each reach model was executed for approximately 2x the modeler-determined steady state time.  Depth grids were produced at intervals ranging from 200-900 seconds depending on the model.  Depth grid print time was determined by attempting to get at least three rasters in the steepest portion of the convergence metric timeseries. From these rasters, several metrics were assessed to identify quasi-steady state. Definitions of the metrics can be found in [[DR-022 - What Metrics Should be Used to Terminate Model Runs]]. Timeseries for each of these metrics at each reach are shown below along with the modeler-determined steady state time.

![[FIG-015.png]]
Values for each metric at the modeler-determined steady state time were interpolated and are shown in the table below.

| Reach | Mean Depth Change | Normalized Depth Change | Relative Depth Change | Coefficient of Variation | Volume Convergence |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 30831 | 2.335e-04 | 7.840e-05 | 4.909e-02 | 6.290e+00 | 1.082e-03 |
| 30868 | 2.573e-07 | 2.408e-07 | 1.490e-05 | 6.233e+01 | 7.143e-06 |
| 30869 | 8.498e-07 | 3.201e-07 | 1.364e-01 | 6.573e+01 | 2.500e-06 |
| 30912 | 4.230e-04 | 1.806e-04 | -4.144e-03 | 7.523e+00 | 1.480e-03 |
| 30913 | 1.108e-03 | 5.857e-04 | 9.142e-02 | 9.439e+00 | 2.860e-02 |
| winooski_composite | 7.170e-04 | 2.473e-04 | 1.090e-01 | 1.734e+00 | 5.017e-03 |
Metric review:
 - Mean Depth Change: Examining the y-axis and the table values of the Mean Depth Change metric, it is clear that this metric varies across orders of magnitude even within this relatively homogeneous setting. Furthermore, the values converge to very low values very early on in the simulation, reducing the sensitivity of this metric (i.e., large changes in time only yield small changes in the metric value).
 > [!Error] Reject
>[[DR-022 - What Metrics Should be Used to Terminate Model Runs]]]] > [[DR-022 - What Metrics Should be Used to Terminate Model Runs#ALT-B - Mean Depth Change (m/s)|ALT-B - Mean Depth Change (m/s)]]


 - Normalized Mean Depth Change: This metric operates over a more consistent range than Mean Depth Change, which is good.  That said, this metric suffers from the same issue where values converge to very low values very early on in the simulation, reducing the sensitivity of this metric.
 > [!Error] Reject
>[[DR-022 - What Metrics Should be Used to Terminate Model Runs]]]] > [[DR-022 - What Metrics Should be Used to Terminate Model Runs#ALT-C - Normalized Mean Depth Change (1/s)|ALT-C - Normalized Mean Depth Change (1/s)]]

 - Relative Depth Change: Generally, the Relative Depth Change metric oscillates around 0 near the modeler defined steady state time.  This behavior is fairly consistent between reaches.  While this shows promise, the signal is very noisy, which may limit our ability to determine steady state via automated procedures.  In the future, a smoothing kernel could be applied across the signal to reduce noise and aid in automated convergence checks.
 > [!Error] Reject
>[[DR-022 - What Metrics Should be Used to Terminate Model Runs]]]] > [[DR-022 - What Metrics Should be Used to Terminate Model Runs#ALT-D - Relative Mean Depth Change (-)|ALT-D - Relative Mean Depth Change (-)]]

 - Coefficient of Variation: Coefficient of Variation is the only metric that increases with time.  This is because as time increases, mean depth changes become smaller at a faster rate than the variance of depth changes decreases.  No trend is readily apparent across all reaches at the modeler-determined steady state point, although further investigation could be performed.  It's worth noting that reach 30912 was a reach that showed slow filling behavior, and it is the only reach where Coefficient of Variation was not rapidly increasing near model convergence time.  This may indicate that this metric could be used as an auxiliary quality check to tell if a reach was still filling/draining at termination time.
 > [!Error] Reject
>[[DR-022 - What Metrics Should be Used to Terminate Model Runs]]]] > [[DR-022 - What Metrics Should be Used to Terminate Model Runs#ALT-F - Depth Change Coefficient of Variation (-)|ALT-F - Depth Change Coefficient of Variation (-)]]

 - Volume Convergence: This metric showed reliable smooth transitions on a well-defined range from 1-0.  Convergence around the 0 value generally occurred later in the simulation than Mean Depth Change and Normalized Mean Depth Change convergence (closer to the modeler-determined steady state time).  While table values for this metric varied over several orders of magnitude, a supplementary analysis (shown below) found that a value of 1e-3 performed well across all reaches.

  - Slope Volume Convergence: This metric does not appear to provide much different information that the volume convergence metric.
 > [!Error] Reject
>[[DR-022 - What Metrics Should be Used to Terminate Model Runs]] > [[DR-022 - What Metrics Should be Used to Terminate Model Runs#ALT-J - Slope Volume Convergence (-)|ALT-J - Slope Volume Convergence (-)]]



Given that the Volume Convergence Metric appeared to perform reliably across reaches, a supplementary analysis was performed to determine a reasonable threshold for this metric to determine quasi steady state.  After some sensitivity, 1e-3 was found to be an acceptable value to balance model convergence with model compute time.  The results of choosing this value for automated steady state determination are compared to the modeler-selected times in the plots below.
![[FIG-016.png]]

![[FIG-017.png]]
![[FIG-018.png]]
![[FIG-019.png]]
![[FIG-020.png]]
![[FIG-021.png]]
