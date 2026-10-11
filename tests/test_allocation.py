import json
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import LineString, MultiLineString, Point

from gas_network import allocate_demand

CRS = "EPSG:32639"


def layers(line_geometries=None, points=None, demands=None):
    line_geometries = line_geometries if line_geometries is not None else [LineString([(0, 0), (10, 0)])]
    points = points if points is not None else [Point(2, 1), Point(7, 1)]
    demands = demands if demands is not None else [4.0, 6.0]
    return (gpd.GeoDataFrame({"Size": [63] * len(line_geometries)}, geometry=line_geometries, crs=CRS),
            gpd.GeoDataFrame({"Demand": demands}, geometry=points, crs=CRS))


def loads(nodes):
    return {(g.x, g.y): value for g, value in zip(nodes.geometry, nodes["load"])}


def test_single_segment_splits_load_evenly():
    nodes, report = allocate_demand(*layers())
    assert loads(nodes) == {(0, 0): 5.0, (10, 0): 5.0}
    assert report["assigned_consumer_rows"] == 2
    assert report["total_difference"] == 0


def test_distinct_consumers_at_same_coordinate_are_all_retained():
    nodes, report = allocate_demand(*layers(points=[Point(2, 1)] * 3, demands=[4, 6, 8]))
    assert loads(nodes) == {(0, 0): 9, (10, 0): 9}
    assert report["assigned_consumer_rows"] == 3


def test_equidistant_consumer_is_counted_once():
    lines, consumers = layers([LineString([(0, 0), (10, 0)]), LineString([(0, 2), (10, 2)])],
                              [Point(5, 1)], [12])
    nodes, report = allocate_demand(lines, consumers)
    assert report["consumers_with_equidistant_pipes"] == 1
    assert report["output_load"] == 12
    assert sorted(nodes["load"]) == [0, 0, 6, 6]
    # Equal-distance selection is repeatable for an unchanged input and environment.
    repeated, _ = allocate_demand(lines, consumers)
    assert loads(nodes) == loads(repeated)


def test_connected_segments_sum_at_shared_endpoint():
    nodes, _ = allocate_demand(*layers(
        [LineString([(0, 0), (10, 0)]), LineString([(10, 0), (20, 0)])],
        [Point(3, 1), Point(17, 1)], [8, 12]))
    assert loads(nodes) == {(0, 0): 4, (10, 0): 10, (20, 0): 6}


def test_crossing_is_split_into_junction():
    nodes, _ = allocate_demand(*layers(
        [LineString([(-10, 0), (10, 0)]), LineString([(0, -10), (0, 10)])],
        [Point(-5, 1)], [10]))
    assert loads(nodes)[(0, 0)] == 5
    assert len(nodes) == 5
    assert nodes["load"].sum() == 10


def test_multiline_and_zero_demand():
    nodes, _ = allocate_demand(*layers(
        [MultiLineString([[(0, 0), (10, 0)], [(10, 0), (20, 0)]])],
        [Point(1, 0)], [0]))
    assert len(nodes) == 3
    assert nodes["load"].sum() == 0


def test_consumer_crs_is_reprojected():
    lines, consumers = layers([LineString([(500000, 4000000), (500100, 4000000)])],
                              [Point(500010, 4000001)], [10])
    expected, _ = allocate_demand(lines, consumers)
    actual, _ = allocate_demand(lines, consumers.to_crs(4326))
    assert loads(expected) == loads(actual)


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf"), "not-a-number"])
def test_invalid_demand_is_rejected(bad):
    with pytest.raises((ValueError, TypeError)):
        allocate_demand(*layers(points=[Point(2, 1)], demands=[bad]))


def test_geographic_crs_is_rejected():
    lines, consumers = layers()
    with pytest.raises(ValueError, match="projected CRS"):
        allocate_demand(lines.to_crs(4326), consumers.to_crs(4326))


def test_empty_consumers_are_rejected():
    lines, consumers = layers()
    with pytest.raises(ValueError, match="empty"):
        allocate_demand(lines, consumers.iloc[:0])


def test_custom_columns():
    lines, consumers = layers()
    nodes, _ = allocate_demand(lines.rename(columns={"Size": "diameter"}),
                               consumers.rename(columns={"Demand": "usage"}),
                               size_column="diameter", demand_column="usage")
    assert nodes["load"].sum() == 10


@pytest.mark.parametrize("extension", ["shp", "gpkg"])
def test_cli_round_trip_and_overwrite_protection(tmp_path, extension):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / f"nodes.{extension}"
    command = [sys.executable, "-m", "gas_network", "--lines", str(root / "data/example/sample_pipes.geojson"),
               "--consumers", str(root / "data/example/sample_consumers.geojson"), "--output", str(output)]
    result = subprocess.run(command, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    nodes = gpd.read_file(output)
    assert loads(nodes) == {(500000, 4000000): 5, (500010, 4000000): 9, (500020, 4000000): 4}
    report = json.loads(output.with_suffix(".report.json").read_text())
    assert report["saved_output_verified"] is True
    before = output.read_bytes()
    repeated = subprocess.run(command, text=True, capture_output=True)
    assert repeated.returncode != 0
    assert output.read_bytes() == before
