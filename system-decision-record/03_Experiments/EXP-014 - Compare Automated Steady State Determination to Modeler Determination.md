## Description

Reach-based hydraulic models require different run durations before they hit quasi–steady-state conditions. Furthermore, there is no single universally accepted definition of “quasi–steady.” In practice, this state may be characterized in several ways, including (1) convergence of outflow to inflow, (2) negligible temporal changes in water surface elevation or depth, or (3) stabilization of other state variables within a defined tolerance. Because of this ambiguity, a metric is required to determine when a simulation has effectively reached quasi-steady conditions and can be terminated.

In this study, a modeler iteratively executes simulations with varying run durations and identifies, based on professional judgment, the point at which the system is considered sufficiently converged. This reference time is then compared against the trigger times produced by candidate convergence metrics. The objective is to assess which metric most consistently and accurately predicts the onset of quasi–steady-state conditions, thereby providing a defensible and automated criterion for terminating model runs.

## Methodology
1. Set up a model run using the decision register.
2. Run the model for a duration that is intentionally longer than expected to reach quasi–steady-state.
3. Review depth grids at each timestep, and identify when the model has stabilized to a suitable degree (subjective)
4. Plot timeseries of the candidate metrics and identify which metric comes closest to the modeler-determined termination point.