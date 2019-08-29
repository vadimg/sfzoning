#!/usr/bin/env python

import json
import os
from collections import defaultdict
from shapely.geometry import shape

from lib.fileutil import data_path, generated_path
from lib.calc.mountain_view import units_per_density_limit, units_per_height, LOT_SIZE
from lib.calc import color, key_stats

with open(data_path('mountain_view.geojson')) as f:
    obj = json.load(f)

for o in obj['features']:
    prop = o['properties']
    zoning = prop['PRODGISGeneralPlanDesignationLANDUSECODE']
    homes_density = units_per_density_limit(zoning)
    homes_height = units_per_height(zoning)

    homes = min(homes_density, homes_height)

    if 0 < homes < 1:
        homes = 1

    prop['zoning'] = zoning
    prop['homes'] = homes
    prop['homes_zoning'] = homes_density
    prop['homes_height'] = homes_height
    prop['fill'] = color(homes)

    print(zoning, round(min(homes_density, homes_height), 1))

stats = key_stats(obj['features'], LOT_SIZE)
stats['city'] = 'Mountain View'
stats['center'] = [-122.0637322335084, 37.39644593970458]
stats['zoom'] = 12

os.makedirs(generated_path('mountain_view'), exist_ok=True)

with open(generated_path('mountain_view/key_data.json'), 'w') as f:
    json.dump(stats, f)

with open(generated_path('mountain_view/density_map.geojson'), 'w') as f:
    json.dump(obj, f)
