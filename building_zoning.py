import ujson
import sys
from collections import namedtuple

from shapely.geometry import shape

Data = namedtuple('Data', 'geo polygon properties')


def dump(filename, features):
    with open(filename, 'w') as f:
        ujson.dump(dict(type='FeatureCollection', features=features), f)


def main():
    num_splits = int(sys.argv[1])
    split_num = int(sys.argv[2])
    start_at = int(sys.argv[3]) if len(sys.argv) >= 4 else 0

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
        if not p.is_valid:
            p = p.buffer(0)
        zones.append(Data(geo=o['geometry'], polygon=p, properties=o['properties']))

    building_zoning = []
    for i, building_obj in enumerate(buildings['features']):
        if i < start_at:
            continue
        print i, '/', len(buildings['features'])

        if i % 5000 == 0:
            dump('generated/building_zoning-%d-of-%d.geojson' % (
                    split_num, num_splits), building_zoning)

        if i % num_splits != split_num - 1:
            continue

        building = shape(building_obj['geometry'])
        properties = building_obj['properties']

        intersects = []
        for zone in zones:
            try:
                intersect = building.intersection(zone.polygon)
            except Exception as e:
                print e
                import pdb;pdb.set_trace()
            if intersect.is_empty:
                continue

            intersects.append((zone.properties, intersect.area))

        if intersects:
            max_i = max(intersects, key=lambda x: x[1])
            print max_i[0]['homes'], properties['resunits']
            building_obj['properties']['zoning'] = max_i[0]

        building_zoning.append(building_obj)

    dump('generated/building_zoning-%d-of-%d.geojson' % (split_num, num_splits), building_zoning)

if __name__ == '__main__':
    main()
