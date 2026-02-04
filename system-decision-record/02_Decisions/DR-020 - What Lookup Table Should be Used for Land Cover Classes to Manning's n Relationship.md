## Description
Only relevant for [[DR-019 - What Source Surface Roughness Data Should be Used for Modeling]].

## Alternatives

### ALT-A - USACE Dictionary
#current
The following lookup table was derived from the [Army Corps of Engineers HEC-RAS guidance](https://www.hec.usace.army.mil/confluence/rasdocs/r2dum/6.6/developing-a-terrain-model-and-geospatial-layers/creating-land-cover-mannings-n-values-and-impervious-layers#id-.CreatingLandCover,Manning%E2%80%99snvalues,and%ImperviousLayersv6.5.Beta-Manning'snCalibrationRegions).
```python
MANNINGS_LC_LOOKUP = {
    11: 0.04,
    21: 0.04,
    22: 0.1,
    23: 0.08,
    24: 0.15,
    31: 0.025,
    41: 0.16,
    42: 0.16,
    43: 0.16,
    52: 0.1,
    71: 0.035,
    81: 0.03,
    82: 0.035,
    90: 0.12,
    95: 0.07,
}
```

### ALT-B - mannings_roughness_generator Dictionary

This repository lists an alternative dictionary, although the source is unclear: https://github.com/mabdazzam/mannings_roughness_generator/tree/main/lookups


## Linked Cases Summary Table

| Alt | Case | Link | Reason |
| --- | --- | --- | --- |
| | | | |

## Decision History
- 2026-02-02: Retroactively document current approach (ALT-A)