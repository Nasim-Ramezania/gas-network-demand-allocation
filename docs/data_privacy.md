# Data privacy

The public example is synthetic: its coordinates and demand values were invented. It is not a renamed, shifted, or anonymized copy of the confidential dataset.

Changing a filename does not anonymize GIS data. Coordinates, attribute tables, connection geometry, original IDs, loads, and sidecar files can reveal information even when names are removed.

## Public package

- Source code, tests, method documentation, and installation instructions.
- `data/example/sample_pipes.geojson` and `sample_consumers.geojson`: invented fixtures.
- Synthetic test results and a description of the local validation procedure.

## Keep local

- Original pipe and consumer files, their sidecar files, and attribute tables.
- Outputs computed from confidential inputs and their JSON diagnostics.
- Screenshots or maps showing real coordinates or identifiable network features.
- Private dataset counts, demand totals, geographic metadata, and connection records.

Use `data/private/` for your own inputs and `output/` for results; both are ignored by Git. The ignore rules also exclude common GIS formats and archive files. Ignore rules do not protect files already committed or forcibly added, so inspect the actual tracked file list before publishing.

Never upload the earlier private-data execution bundle as part of this public project. If a confidential file was already pushed, removing it from the current folder does not remove it from Git history. Review the repository history and address that exposure separately.
