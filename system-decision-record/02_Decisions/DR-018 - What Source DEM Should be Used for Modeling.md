## Description
Topographic data is needed for model creation. What source should be used for topographic data? Source consistency is essential here so that national libraries can be produced without region-specific alterations.
## Alternatives

### ALT-A - USGS 3DEP
#current 

USGS 3DEP is the first choice because of its authoritativeness as well as availability.

Source: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/USGS_Seamless_DEM_13.vrt

### ALT-B - FATHOM+ DEM

USGS 3DEP DEM has tile boundary effects at tile boundary which a lot of the time happens to be at state boundaries which themselves are at Rivers. FATHOM+DEM was compared at same location and had better blended edges. 

Update: It seems that USGS 3DEP has updated dataset and some of those effects have gone away and results are better than FATHOM+ DEM

## Decision History
- 2026-02-02: Retroactively document current approach (ALT-A)
