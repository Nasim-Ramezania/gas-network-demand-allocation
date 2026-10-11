"""Nearest-segment assignment with equal endpoint allocation."""
from __future__ import annotations

import math

import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import unary_union


def allocate_demand(
    lines: gpd.GeoDataFrame,
    consumers: gpd.GeoDataFrame,
    *,
    size_column: str = "Size",
    demand_column: str = "Demand",
) -> tuple[gpd.GeoDataFrame, dict]:
    """Return endpoint loads and diagnostics without modifying the input layers.

    Each input consumer row is assigned once. On exact distance ties, the
    lowest generated segment ID wins. Half of each segment's demand is placed
    at each endpoint, then coincident endpoints are aggregated by WKT.
    """
    if lines.empty or consumers.empty:
        raise ValueError("Input layers must not be empty.")
    if size_column not in lines:
        raise ValueError(f"Missing pipe-size column: {size_column}")
    if demand_column not in consumers:
        raise ValueError(f"Missing consumption column: {demand_column}")
    if lines.crs is None or consumers.crs is None:
        raise ValueError("Both input layers must have a CRS.")
    if not lines.crs.is_projected:
        raise ValueError("Use a projected CRS for distance calculations.")
    if lines.crs != consumers.crs:
        consumers = consumers.to_crs(lines.crs)
    for name, layer in (("lines", lines), ("consumers", consumers)):
        if (layer.geometry.isna().any() or layer.geometry.is_empty.any()
                or not layer.geometry.is_valid.all()):
            raise ValueError(f"{name}: missing, empty, or invalid geometry.")
    if not lines.geom_type.isin(["LineString", "MultiLineString"]).all():
        raise ValueError("The pipe layer must contain line geometries.")
    if not consumers.geom_type.eq("Point").all():
        raise ValueError("The consumer layer must contain point geometries.")
    if lines[size_column].isna().any():
        raise ValueError("Pipe size must not be missing.")
    demand = pd.to_numeric(consumers[demand_column], errors="raise")
    if demand.isna().any() or not demand.map(math.isfinite).all():
        raise ValueError("Demand contains missing or non-finite values.")
    if demand.lt(0).any():
        raise ValueError("Demand must not be negative.")

    points = gpd.GeoDataFrame(
        {"_consumer_id": range(len(consumers)), "_demand": demand.to_numpy()},
        geometry=consumers.geometry.reset_index(drop=True), crs=lines.crs,
    )
    input_total = math.fsum(points["_demand"])
    dissolved = lines.dissolve(by=size_column).reset_index()
    merged = unary_union(dissolved.geometry)
    if merged.geom_type == "LineString":
        segments = [merged]
    elif merged.geom_type == "MultiLineString":
        segments = list(merged.geoms)
    else:
        raise ValueError("Unexpected geometry after merging lines.")
    if not segments or any(g.is_empty or g.length == 0 for g in segments):
        raise ValueError("The processed network contains empty or zero-length lines.")
    pipes = gpd.GeoDataFrame(geometry=segments, crs=lines.crs)
    pipes["line_id"] = range(1, len(pipes) + 1)
    joined = gpd.sjoin_nearest(points, pipes[["line_id", "geometry"]],
                              how="left", distance_col="snap_dist")
    if joined["line_id"].isna().any():
        raise ValueError("Some consumers could not be assigned to a pipe.")
    tie_count = int(joined.groupby("_consumer_id").size().gt(1).sum())
    assigned = (joined.sort_values(["_consumer_id", "snap_dist", "line_id"])
                .drop_duplicates("_consumer_id", keep="first").copy())
    if len(assigned) != len(points):
        raise RuntimeError("Consumer assignment count does not match input.")
    loads = assigned.groupby("line_id")["_demand"].sum().rename("total_load").reset_index()
    pipes = pipes.merge(loads, on="line_id", how="left", validate="one_to_one")
    pipes["total_load"] = pipes["total_load"].fillna(0.0)
    endpoints = []
    for _, row in pipes.iterrows():
        coords = list(row.geometry.coords)
        for coord in (coords[0], coords[-1]):
            endpoints.append({"wkt": Point(coord).wkt, "load": row["total_load"] / 2.0})
    grouped = pd.DataFrame(endpoints).groupby("wkt", as_index=False)["load"].sum()
    grouped["geometry"] = grouped["wkt"].map(wkt.loads)
    nodes = gpd.GeoDataFrame(grouped.drop(columns="wkt"), geometry="geometry", crs=lines.crs)
    total = math.fsum(nodes["load"])
    if not math.isclose(input_total, total, rel_tol=1e-10, abs_tol=1e-8):
        raise RuntimeError(f"Load mismatch: input={input_total}, output={total}")
    report = {
        "input_line_features": len(lines), "processed_segments": len(pipes),
        "consumer_rows": len(points), "assigned_consumer_rows": len(assigned),
        "consumers_with_equidistant_pipes": tie_count,
        "output_nodes": len(nodes), "input_demand": input_total,
        "output_load": total, "total_difference": total - input_total,
        "maximum_nearest_pipe_distance": float(assigned["snap_dist"].max()),
        "distance_unit": lines.crs.axis_info[0].unit_name,
        "crs": str(lines.crs),
        "allocation_rule": "nearest segment; exact ties use lowest generated line_id; half to each endpoint",
    }
    return nodes, report
