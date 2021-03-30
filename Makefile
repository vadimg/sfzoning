all: sf mountain_view

.PHONY: all clean sf mountain_view

clean:
	rm -rf generated/*

clean_maps:
	find . | grep density_map | xargs rm

sf: generated/sf/density_map.geojson

sf_illegal: generated/sf/illegal_homes.geojson

prop_e: generated/sf/prop_e.geojson

mountain_view: generated/mountain_view/density_map.geojson

generated/sf/illegal_homes.geojson: generated/sf/lot_building_zoning.geojson
	ENV/bin/python ./lib/sf/illegal_homes.py

generated/sf/density_map.geojson: generated/sf/zoning_height.geojson
	ENV/bin/python ./lib/sf/map.py

generated/sf/zoning_height.geojson:
	ENV/bin/python ./lib/sf/zoning_height_map.py

generated/sf/lot_zoning.geojson: generated/sf/density_map.geojson
	ENV/bin/python ./lib/sf/lot_zoning.py

generated/sf/lot_building_zoning.geojson: generated/sf/lot_zoning.geojson
	ENV/bin/python ./lib/sf/lot_buildings.py

generated/sf/prop_e.geojson: generated/sf/lot_building_zoning.geojson
	ENV/bin/python ./lib/sf/prop_e.py

generated/mountain_view/density_map.geojson:
	ENV/bin/python ./lib/mountain_view/map.py
