from shapely.geometry import shape

from fileutil import load, dump
from polygon_index import PolygonIndex


def main():
    zones = load('generated/density_map.geojson')

    index = PolygonIndex()
    for i, obj in enumerate(zones):
        print '%s / %s' % (i + 1, len(zones))
        index.add_obj(obj)

    lots = load('data/lots.geojson')

    lot_zoning = []
    not_found = []
    for i, obj in enumerate(lots):
        print '%s / %s' % (i + 1, len(lots))

        if i % 10000 == 0:
            dump('generated/lot_zoning.geojson', lot_zoning)
            dump('generated/zone_not_found_for_lot.geojson', not_found)

        lot_poly = shape(obj['geometry'])
        intersecting = index.intersecting(lot_poly)

        intersects = []
        for zone in intersecting:
            intersect = lot_poly.intersection(zone.polygon)
            if intersect.is_empty:
                continue

            intersects.append((zone.data['properties'], intersect.area))

        if not intersects:
            # this is probably a vacant thingy
            print 'ZONE NOT FOUND', obj
            not_found.append(obj)
            continue

        max_i = max(intersects, key=lambda x: x[1])
        print max_i[0]['homes'], obj['properties']['resunits']
        obj['properties']['zoning'] = max_i[0]

        lot_zoning.append(obj)


    dump('generated/lot_zoning.geojson', lot_zoning)
    dump('generated/zone_not_found_for_lot.geojson', not_found)


if __name__ == '__main__':
    main()
