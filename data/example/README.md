# Synthetic example

These coordinates and demands were invented for demonstration and are not taken from the private dataset. Both GeoJSON files declare projected CRS EPSG:32639. They are GIS interchange fixtures for GDAL/GeoPandas, not RFC 7946 longitude/latitude web-map feeds.

The network contains two connected 10-metre segments. Consumer demands of 4 and 6 share a coordinate near the first segment. A third consumer with demand 8 lies near the second segment.

| Node easting | Node northing | Expected load |
|---|---|---|
| 500000 | 4000000 | 5 |
| 500010 | 4000000 | 9 |
| 500020 | 4000000 | 4 |

Total input and output demand: 18 (arbitrary consistent demand units).
