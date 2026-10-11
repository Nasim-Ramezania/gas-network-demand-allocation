# Method and limitations

For each resulting segment j, let C(j) be the consumer rows assigned to it. Its demand is the sum of Demand over C(j). Each endpoint receives half that sum; node loads are the sum of all endpoint contributions at the same coordinate.

Every valid consumer row has one assignment. Therefore, summing all endpoint contributions recovers the input demand, subject to floating-point arithmetic. Both pre-export and post-export totals use `math.isclose` with relative tolerance `1e-10` and absolute tolerance `1e-8`.

## Interpretation

- **Nearest-segment assumption:** geographical proximity is used in place of actual service-connection records.
- **No maximum distance:** even a far-away consumer is assigned. The diagnostics expose the maximum nearest-pipe distance and its CRS unit; review it against the study context.
- **Tie rule:** exact distance ties use the lowest generated segment ID. These are processing IDs, not original pipe identifiers, and should not be treated as stable across changed inputs or geometry-library versions. A near-tie tolerance is not applied.
- **Half to each endpoint:** demand is not weighted by the consumer's position along a segment.
- **Geometric topology:** union splits intersecting lines, including crossings that may not physically connect. Near-coincident endpoints are not snapped together. Coordinate and topology cleaning remain separate tasks.
- **Precision and dimensions:** WKT endpoint keys follow the original script's serialization. No explicit spatial snapping tolerance or Z-aware physical connectivity model is provided. Validate unusual high-precision or 3D data separately.
- **Size field:** size groups participate in the dissolve step, but the subsequent union loses the size attributes. Coincident overlapping pipes may collapse geometrically. The output is a node-load layer, not a pipe inventory.
- **Closed segments:** both endpoint contributions can land on the same coordinate; their sum is retained.
- **Numeric validation:** negative, missing, infinite, or nonnumeric demand is rejected. Extremely large finite values can still overflow aggregates and fail the conservation check.

## Changes from the initial script

The algorithm and default fields (`Size`, `Demand`) are retained. The packaged version separates computation from file handling, accepts paths and field names through a CLI, supports GeoPackage output, refuses to overwrite existing output files, and writes structured diagnostics. It includes publicly shareable synthetic inputs and automated tests.

The original private-data result was checked node by node against the packaged implementation before preparing this repository. This parity check preserves the tested allocation behaviour; it does not remove the modelling assumptions above.
