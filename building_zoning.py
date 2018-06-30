import ujson
from collections import namedtuple

from shapely.geometry import shape
import shapely

Data = namedtuple('Data', 'polygon properties')

def main():
    with open('data/buildings.geojson') as f:
        buildings = ujson.load(f)

    print buildings['features'][0]['properties']['resunits']
    print len(buildings['features'])

    with open('generated/density_map.geojson') as f:
        zones_obj = ujson.load(f)

    print zones_obj['features'][0]['properties']['homes']


    zones = []
    for i, o in enumerate(zones_obj['features']):
        p = shape(o['geometry'])
        zones.append(Data(polygon=p, properties=o['properties']))

    building_zoning = []
    for i, building_obj in enumerate(buildings['features']):
        print i, '/', len(buildings['features'])
        building = shape(building_obj['geometry'])
        properties = building_obj['properties']

        intersects = []
        for zone in zones:
            intersect = p.intersection(zone.polygon)
            if intersect.is_empty:
                continue

            intersects.append((zone.properties, intersect.area))

        max_i = max(intersects, key=lambda x: x[1])
        print max_i[0]['homes'], properties['resunits']

        building_obj['properties']['zoning'] = max_i[0]
        building_zoning.append(building_obj)

    with open('generated/building_zoning.geojson', 'w') as f:
        ujson.dump(dict(type='FeatureCollection', features=building_zoning), f)

main()
