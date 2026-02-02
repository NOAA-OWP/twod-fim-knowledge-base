## Description

Run a model using the methodology as described in the Decision Register. Specifically, the model domain is created from the reach divide geometry.

## Methodology
1. Build a model following Decision Register methodology.
	1. At the time of writing, the decision register defines model domain development as
		1. Create an inflow line 25% up the upstream mainstem flowpath with width 100 meters.
		2. Extract the reach divide for the modeled reach from the hydrofabric
		3. Take the combined bounding box of both geometries.  Buffer them by one cell resolution, and use the buffered geometry for the model domain.
2. Compare with Benchmark FIM