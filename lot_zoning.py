import ujson
import sys
from collections import namedtuple

import shapely
from shapely.geometry import shape, Polygon

Data = namedtuple('Data', 'geo polygon properties')


def dump(filename, features):
    with open(filename, 'w') as f:
        ujson.dump(dict(type='FeatureCollection', features=features), f)

def poly2json(polygon):
    return dict(
        type='Feature',
        properties={},
        geometry=shapely.geometry.geo.mapping(polygon),
    )

ROUNDNUM = 3
def roundpoint(point):
    return (round(point.x, ROUNDNUM), round(point.y, ROUNDNUM))


def inc(n, amt):
    return round(n + amt * (10**-ROUNDNUM), ROUNDNUM)

def square(point):
    return Polygon([
        (inc(point[0], 0), inc(point[1], 0)),
        (inc(point[0], 0), inc(point[1], 1)),
        (inc(point[0], 1), inc(point[1], 1)),
        (inc(point[0], 1), inc(point[1], 0)),
    ])


def squares(point):
    ret = []
    for xr in (-1, 0, 1):
        for yr in (-1, 0, 1):
            r = (inc(point[0], xr), inc(point[1], yr))
            ret.append(square(r))
    return ret


def all_squares(polygon):
    rp = roundpoint(polygon.representative_point())
    ret = []
    search_list = squares(rp)
    visited = set()
    while search_list:
        sq = search_list.pop()
        if sq.bounds in visited:
            continue

        visited.add(sq.bounds)
        if sq.intersects(polygon):
            ret.append(sq)
            new_sq = squares((sq.bounds[0], sq.bounds[1]))
            new_sq = [x for x in new_sq if x.bounds not in visited]
            search_list.extend(new_sq)
    return ret

class PolyIndex(object):
    MapValue = namedtuple('MapValue', 'polygon data')

    def __init__(self):
        self._index = {}

    def add_obj(self, obj):
        polygon = shape(obj['geometry'])
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        self.add_polygon(polygon, obj)

    def add_polygon(self, polygon, data):
        sqs = all_squares(polygon)
        for sq in sqs:
            self._index.setdefault(sq.bounds, []).append(self.MapValue(polygon=polygon, data=data))

    def intersecting(self, polygon):
        ret = {}

        sqs = all_squares(polygon)
        for sq in sqs:
            others = self._index.get(sq.bounds, [])
            for val in others:
                wkt = val.polygon.wkt
                if wkt in ret:
                    continue

                if polygon.intersects(val.polygon):
                    ret[wkt] = val

        return ret.values()


def main():
    with open('generated/density_map.geojson') as f:
        zones_obj = ujson.load(f)

    obj = sorted(zones_obj['features'], key=lambda x: len(x['geometry']))[-1]
    index = PolyIndex()
    for i, obj in enumerate(zones_obj['features']):
        print '%s / %s' % (i + 1, len(zones_obj['features']))
        index.add_obj(obj)

    with open('data/lots.geojson') as f:
        lots = ujson.load(f)

    lot_zoning = []
    not_found = []
    for i, obj in enumerate(lots['features']):
        print '%s / %s' % (i + 1, len(lots['features']))

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
