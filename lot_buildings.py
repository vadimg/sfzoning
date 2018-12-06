from shapely.geometry import shape

from fileutil import load, dump
from polygon_index import PolygonIndex


def main():
    lots = load('generated/building_zoning.geojson')

    index = PolygonIndex()
    for i, obj in enumerate(lots):
        print '%s / %s' % (i + 1, len(lots))
        index.add_obj(obj)

    buildings = load('data/buildings.geojson')

    not_found = []
    multiple_found = []

    def dumpall():
        dump('generated/lot_buildings_zoning.geojson', lots)
        dump('generated/building_not_found_for_lot.geojson', not_found)
        dump('generated/multiple_lots_per_building.geojson', multiple_found)

    for i, obj in enumerate(buildings):
        print '%s / %s' % (i + 1, len(buildings))

        if i % 10000 == 0:
            dumpall()

        poly = shape(obj['geometry'])
        intersecting = index.intersecting(poly)

        intersects = []
        for lot in intersecting:
            intersect = poly.intersection(lot.polygon)
            if intersect.is_empty:
                continue

            intersects.append((lot.data, intersect.area))

        if not intersects:
            print 'LOT NOT FOUND', obj
            not_found.append(obj)
            continue

        print len(intersects)
        if len(intersects) != 1:
            multiple_found.extend([x[0] for x in intersects])
            multiple_found.append(lot.data)

        max_i = max(intersects, key=lambda x: x[1])
        max_i[0]['properties'].setdefault('buildings', []).append(obj)


    dumpall()


if __name__ == '__main__':
    main()
