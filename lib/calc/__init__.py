import functools
from collections import defaultdict
from shapely.geometry import shape

import shapely.ops as ops
from area import area as pyarea

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


def round_units(units):
    # super-low density counts as 1 home as long as any housing is allowed
    if 0 < units < 1:
        return 1
    return int(units)


def color(units):
    units = round_units(units)
    if units > 20:
        return colors[max(colors.keys())]

    while True:
        ret = colors.get(units)
        if ret is not None:
            return ret
        units -= 1


def sq_ft(geom):
    area = 0
    if geom['type'] == 'MultiPolygon':
        # pyarea doesn't support MultiPolygon, but all it is is this:
        for poly in geom['coordinates']:
            area += pyarea({
                'type': 'Polygon',
                'coordinates': poly,
            })
    else:
        area = pyarea(geom)

    return area * SQ_METER_TO_SQ_FEET


def key_stats(features, *, lot_size, all_area_denom):
    affordable_sqft = 0
    residential_sqft = 0

    home_areas = defaultdict(int)
    for o in features:
        polygon = shape(o['geometry'])
        area = polygon.area
        homes = o['properties']['homes']

        if homes > 0:
            residential_sqft += area
        if homes >= 50 / (10e3 / lot_size):
            affordable_sqft += area

        home_areas[round_units(homes)] += area

    non_os_area = sum(v for k, v in home_areas.items() if k >= 0)
    all_area = sum(home_areas.values())

    apt_legal_area = 0
    apt_illegal_area = 0
    apt5_legal_area = 0
    dat = []
    for m in sorted(home_areas.keys()):
        percentage = 100.0 * home_areas[m] / all_area
        dat.append({
            "homes": m,
            "percentage": percentage,
            "color": color(m),
        })

        if m > 2:
            apt_legal_area += home_areas[m]
        if m >= 5:
            apt5_legal_area += home_areas[m]

        if m > 20:
            # the rest will be labeled "> 20"
            break

    total_percent = sum(x['percentage'] for x in dat[:-1])
    dat[-1]['percentage'] = 100 - total_percent

    denom = all_area if all_area_denom else non_os_area

    return dict(
        lot_size=lot_size,
        key=dat,
        apt_illegal_pct=100 - 100 * apt_legal_area / denom,
        apt5_illegal_pct=100 - 100 * apt5_legal_area / denom,
        affordable_illegal_resi_pct=100 - 100 * affordable_sqft / residential_sqft,
        affordable_illegal_pct=100 - 100 * affordable_sqft / denom,
    )
