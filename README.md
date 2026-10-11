# Gas Network Demand Allocation
[![Tests](https://github.com/Nasim-Ramezania/gas-network-demand-allocation/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Nasim-Ramezania/gas-network-demand-allocation/actions/workflows/tests.yml)
A reproducible Python GIS workflow that assigns consumer demand to pipe-network endpoints. It uses GeoPandas and Shapely to associate each consumer with a nearest network segment, split the segment's demand equally between its endpoints, and sum loads at coincident nodes.

**This is a spatial preprocessing project, not a gas-flow or pressure simulation.**

## What this project demonstrates

- Validation of geometry types, coordinate reference systems (CRS), and numeric demand.
- Network segmentation and nearest-neighbour spatial assignment.
- Preservation of distinct consumer rows, including consumers at the same location.
- Explicit handling of equidistant pipes to avoid double counting.
- Conservation checks before export and after re-reading the saved output.
- Automated tests and a GitHub Actions workflow configured for Python 3.12 on Linux and Windows.

## Quick start — Windows / VS Code

Open the repository folder in VS Code, then run these commands in PowerShell. Calling the virtual environment's Python directly avoids needing to change PowerShell execution policy.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m gas_network --lines data/example/sample_pipes.geojson --consumers data/example/sample_consumers.geojson --output output/nodes_with_load.shp
```

If the `py` launcher is unavailable, use `python -m venv .venv` with Python 3.12 selected.

For macOS or Linux:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
.venv/bin/python -m gas_network --lines data/example/sample_pipes.geojson --consumers data/example/sample_consumers.geojson --output output/nodes_with_load.shp
```

The example data are entirely synthetic. The expected node loads are **5, 9, and 4**, with a total demand of **18**. Open `output/nodes_with_load.shp` in QGIS and inspect its `load` field. Keep the `.shp`, `.shx`, `.dbf`, `.prj`, and `.cpg` files together. Use an output ending in `.gpkg` for a single-file GeoPackage instead. Existing outputs are not overwritten; choose a new filename to run again.

## Use your own data

Place local datasets in `data/private/` (ignored by Git), keeping all Shapefile sidecar files together. Then run:

```powershell
.\.venv\Scripts\python.exe -m gas_network --lines data/private/line.shp --consumers data/private/consumer.shp --output output/my_nodes.shp --size-column Size --demand-column Demand
```

| Input | Requirement |
|---|---|
| Pipes | Nonempty, valid LineString / MultiLineString geometries; projected CRS; nonmissing `Size` |
| Consumers | Nonempty, valid Point geometries; declared CRS; finite, nonnegative numeric `Demand` |
| Demand units | Consistent across all input rows; output `load` retains the same unit |
| Distance units | Taken from the pipe CRS; projected coordinates are not necessarily metres |

Consumers are reprojected to the pipe CRS when necessary. Choose a projection suitable for the study area. Missing or invalid demand causes an error rather than silently becoming zero.

## Method

1. Validate inputs and align CRS.
2. Dissolve pipes by size, then apply a geometric union to split at intersections.
3. Assign each **consumer row** to one nearest resulting segment. If multiple segments are exactly equidistant, choose the lowest generated `line_id`.
4. Sum consumer demand per segment and allocate half to each endpoint.
5. Aggregate coincident endpoints and check that total demand is conserved.
6. Export, re-read, and verify the saved node count, CRS, and total load. Write a JSON diagnostics report next to the output.

See [method and limitations](docs/method.md) and [validation results](docs/validation.md).

## Validation

The workflow and packaged implementation were also checked locally against a confidential dataset, including node-by-node output comparison. Those data, outputs, exact counts, demand totals, geographic metadata, and distance diagnostics are excluded from this public package.

The included synthetic fixtures and tests provide a reproducible public example. Automated tests and the synthetic command-line example passed in GitHub Actions on both Linux and Windows using Python 3.12.

See [data privacy](docs/data_privacy.md) before adding any dataset.

## Repository layout

```text
src/gas_network/     Allocation function and command-line interface
tests/              Hand-checkable scenarios and export round-trip tests
data/example/       Synthetic input data only
docs/               Method, assumptions, and validation evidence
.github/workflows/  Linux / Windows test configuration
```

## Scope and limitations

Nearest geometry is a modelling assumption; it does not prove the consumer's actual pipe connection. Equal endpoint allocation is also an assumption. The workflow does not solve pressure, flow, capacity, or an optimization problem. Geometric crossings are treated as connections, and pipe-size attributes do not survive as output node attributes. See the method document before interpreting the result as a physical network.
