#!/bin/bash

mkdir -p data

curl 'https://data.sfgov.org/api/geospatial/xvjh-uu28?method=export&format=GeoJSON' > data/zoning.geojson
curl 'https://data.sfgov.org/api/geospatial/iddb-5nzh?method=export&format=GeoJSON' > data/height.geojson
