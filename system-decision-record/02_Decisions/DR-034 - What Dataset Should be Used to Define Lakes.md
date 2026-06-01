## Description
The network modification at lakes (see [[DR-007 - How to Modify the Reach Network at Lakes]]) needs a polygon dataset that delineates the lake area used to remove/trim reaches, the `dead pool polygon`. This decision is about where that dataset comes from.

A `dead pool polygon` is intended to be smaller than the full-pool waterbody.

## Alternatives

### ALT-A - Shrink an Existing Waterbody Dataset
#current

Start from an existing national waterbody layer (e.g. NHD / NHDPlus Waterbodies, as used in [[Case-013 - Large Inland Waterbody]]) and shrink each polygon by some criteria to approximate the dead pool. Elevation for the polygon is then assigned separately, see [[DR-035 - What Should be Lower Bound for Lake Stages]].

Reuses an authoritative, maintained dataset and avoids a large data-production effort.

### ALT-B - Build Our Own Lake Polygon Dataset from the DEM
Derive lake polygons directly from the DEM with a delineation algorithm, sourcing an initial candidate list from somewhere (TBD) and growing/extracting the polygon from terrain.

Judged a significant undertaking: it requires an initial seed list, a delineation algorithm, and validation at national scale. Not pursued for now.

## Open Questions
- Which existing dataset (NHD vs NHDPlus vs other) and at what scale.
- The shrink criteria used to go from full-pool polygon to dead pool polygon.

## Decision History
- 2026-05-28: Drafted from meeting notes. ALT-A favored; ALT-B set aside as a significant undertaking.
