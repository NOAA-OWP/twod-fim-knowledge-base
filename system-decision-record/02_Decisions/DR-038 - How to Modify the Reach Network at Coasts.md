#terminal-reaches #network-modification
## Description
Define how the reach network is modified where it approaches coasts during the network modification phase. The goal is to stop modeling reach hydraulics near coasts where coastal models should provide FIMs.

## Alternatives

### ALT-A - Omit Reaches where Reach overlaps NOAA Tidal Surface Coverage
#current

1. Download NOAA tidal surface coverage (MHHW raster footprint)
   https://www.fisheries.noaa.gov/inport/item/48104
   https://coast.noaa.gov/slrdata/Tidal_Surfaces/index.html
2. Intersect reaches with the NOAA tidal surface extent
3. Flag reaches within tidal surface coverage and drop them

## Decision History
- 2026-05-28: Drafted from meeting with developers
