#!/bin/bash

mkdir -p data

curl 'https://data.sfgov.org/api/geospatial/3i4a-hu95?method=export&format=GeoJSON' > data/zoning.geojson
curl 'https://data.sfgov.org/api/geospatial/h6dm-b62f?method=export&format=GeoJSON' > data/height.geojson
curl 'https://data.sfgov.org/api/geospatial/us3s-fp9q?method=export&format=GeoJSON' > data/lots.geojson
curl 'https://data.sfgov.org/api/geospatial/ynuv-fyni?method=export&format=GeoJSON' > data/buildings.geojson
curl 'https://data.sfgov.org/api/views/wv5m-vpq2/rows.csv?accessType=DOWNLOAD' > data/home_values.csv

# mountain view data
curl 'https://opendata.arcgis.com/datasets/f9aced0c78b446f99d43653512b402d6_0.geojson' > data/mountain_view.geojson

# historical SF data
curl 'https://data.sfgov.org/api/geospatial/prs8-k8k3?method=export&format=GeoJSON' > data/zoning_height_2000.geojson
curl 'https://data.sfgov.org/api/geospatial/w3j2-4hed?method=export&format=GeoJSON' > data/zoning_2010.geojson
curl 'https://data.sfgov.org/api/geospatial/ti28-5szz?method=export&format=GeoJSON' > data/height_2010.geojson
