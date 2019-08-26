import functools
from collections import defaultdict
from shapely.geometry import shape

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


def key_stats(features):
    affordable_sqft = 0
    residential_sqft = 0

    home_areas = defaultdict(int)
    for o in features:
        polygon = shape(o['geometry'])
        area = polygon.area
        homes = o['properties']['homes']

        if homes > 0:
            residential_sqft += area
        if homes >= 12.5:
            affordable_sqft += area

        home_areas[int(homes)] += area

    non_os_area = sum(v for k, v in home_areas.items() if k >= 0)
    all_area = sum(home_areas.values())

    apt_illegal_area = 0
    apt5_illegal_area = 0
    dat = []
    for m in sorted(home_areas.keys()):
        percentage = 100.0 * home_areas[m] / all_area
        dat.append({
            "homes": m,
            "percentage": percentage,
            "color": color(m),
        })

        if m >= 0:
            if m <= 2:
                apt_illegal_area += home_areas[m]
            if m <= 5:
                apt5_illegal_area += home_areas[m]

        if m > 20:
            # the rest will be labeled "> 20"
            break

    total_percent = sum(x['percentage'] for x in dat)
    dat[-1]['percentage'] = 100 - total_percent

    return dict(
        key=dat,
        apt_illegal_pct=100 * apt_illegal_area / non_os_area,
        apt5_illegal_pct=100 * apt5_illegal_area / non_os_area,
        affordable_illegal_resi_pct=100 - 100 * affordable_sqft / residential_sqft,
        affordable_illegal_pct=100 - 100 * affordable_sqft / non_os_area,
    )
