## Description

Run a model using the methodology as described in the Decision Register. Instead of using the default inflow boundary line, try several alternatives.

## Methodology
1. Build a model following Decision Register methodology.
2. Add new boundary conditions for the following geometries.
	1. A point at the `reach start`
	2. A 100-meter wide line 25% upstream along the `upstream mainstem`
	3. Perpendicular Line at the `Reach Start`
3. Check for artifacts of boundary geometry in water surface elevation rasters.