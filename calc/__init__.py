import functools

import shapely.ops as ops
import pyproj

METER_TO_FEET = 3.280839895
SQ_METER_TO_SQ_FEET = METER_TO_FEET ** 2

COLORS = """
-1	gray
0	#3b0000
1	#950004
2	#c60003
3	#ff6e00
4	#ffbb00
5	#ffff00
6	#deec00
7	#bed900
10	#9ec500
12	#7eb100
15	#609e00
17	#428c00
20	#207700
22	#006400
"""

colors = {}
for l in COLORS.split('\n'):
    if l.strip():
        units, color = l.split('\t')
        colors[int(units)] = color


def color(units):
    units = int(units)
    if units > 20:
        return colors[max(colors.keys())]

    while True:
        ret = colors.get(units)
        if ret is not None:
            return ret
        units -= 1


def sq_ft(geom):
    geom_area = ops.transform(
        functools.partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(
                proj='aea',
                lat1=geom.bounds[1],
                lat2=geom.bounds[3])),
        geom)
    projected_area = geom_area.area
    return projected_area * SQ_METER_TO_SQ_FEET
