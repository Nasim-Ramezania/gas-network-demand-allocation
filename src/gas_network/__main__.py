"""Command-line interface: python -m gas_network --help."""
import argparse
import json
import math
from pathlib import Path

import geopandas as gpd

from .allocation import allocate_demand


def main():
    parser = argparse.ArgumentParser(description="Allocate consumer demand to network endpoints.")
    parser.add_argument("--lines", type=Path, required=True)
    parser.add_argument("--consumers", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New .shp or .gpkg output")
    parser.add_argument("--size-column", default="Size")
    parser.add_argument("--demand-column", default="Demand")
    args = parser.parse_args()
    suffix = args.output.suffix.lower()
    if suffix not in {".shp", ".gpkg"}:
        parser.error("--output must end in .shp or .gpkg")
    report_path = args.output.with_suffix(".report.json")
    # Prevent accidental replacement of inputs or existing output bundles.
    candidates = [args.output, report_path]
    if suffix == ".shp":
        candidates += [args.output.with_suffix(s) for s in (".shx", ".dbf", ".prj", ".cpg")]
    if any(path.exists() for path in candidates):
        parser.error("Output already exists. Choose a new output filename.")
    nodes, report = allocate_demand(
        gpd.read_file(args.lines), gpd.read_file(args.consumers),
        size_column=args.size_column, demand_column=args.demand_column,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    nodes.to_file(args.output, driver="ESRI Shapefile" if suffix == ".shp" else "GPKG", index=False)
    saved = gpd.read_file(args.output)
    saved_total = math.fsum(saved["load"])
    if (len(saved) != len(nodes) or saved.crs != nodes.crs or
            not math.isclose(report["input_demand"], saved_total, rel_tol=1e-10, abs_tol=1e-8)):
        raise RuntimeError("Saved output failed the load/count/CRS check.")
    report.update(saved_output_load=saved_total, saved_output_verified=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
