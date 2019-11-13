#!/bin/bash

mkdir -p data

curl 'https://data.sfgov.org/api/geospatial/xvjh-uu28?method=export&format=GeoJSON' > data/zoning.geojson
curl 'https://data.sfgov.org/api/geospatial/iddb-5nzh?method=export&format=GeoJSON' > data/height.geojson
curl 'https://data.sfgov.org/api/geospatial/us3s-fp9q?method=export&format=GeoJSON' > data/lots.geojson
curl 'https://data.sfgov.org/api/geospatial/ynuv-fyni?method=export&format=GeoJSON' > data/buildings.geojson
curl 'https://data.sfgov.org/api/views/wv5m-vpq2/rows.csv?accessType=DOWNLOAD' > data/home_values.csv
curl 'https://opendata.arcgis.com/datasets/f9aced0c78b446f99d43653512b402d6_0.geojson' > data/mountain_view.geojson
