from collections import namedtuple

from shapely.geometry import shape, Polygon


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


class PolygonIndex(object):
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


