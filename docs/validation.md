# Validation record

Validation date: 2026-10-11 (UTC). Executed locally on Linux with Python 3.12. Windows has not yet been tested; the repository includes a GitHub Actions matrix to run the suite on both systems after publication.

## Automated tests

Command: `python -m pytest -q`

Observed result: **16 passed in 2.11s**.

Covered scenarios:

- A hand-calculated single segment.
- Multiple independent consumer rows at identical coordinates.
- An equidistant consumer counted exactly once.
- Summed loads at a shared endpoint.
- A crossing split into a junction.
- Multipart geometry and zero demand.
- Consumer CRS reprojection.
- Negative, NaN, infinite, and nonnumeric demand rejection.
- Geographic pipe CRS and empty consumer-layer rejection.
- Custom input column names.
- CLI Shapefile and GeoPackage export/re-read checks and overwrite protection.

The synthetic CLI example produced three nodes with loads 5, 9, and 4; input and output totals were both 18.

## Confidential-data validation

The original script and packaged implementation were compared locally on a confidential dataset. The resulting node loads matched. An independent calculation also checked allocation arithmetic by explicitly computing distances from every consumer to every processed segment and summing endpoint contributions.

No confidential input, output, identifying attribute, exact dataset statistic, location metadata, or private diagnostic report is included here. Publicly reproducible evidence is provided by the synthetic fixtures and tests above. Local private-data validation is not a publicly reproducible benchmark or hydraulic validation.

## Runtime versions

GeoPandas 1.2.0; Shapely 2.2.0; pandas 2.2.3; pyogrio 0.13.0; pyproj 3.8.0; NumPy 2.3.5; pytest 9.1.1. Runtime GIS dependencies are pinned in `pyproject.toml`.
