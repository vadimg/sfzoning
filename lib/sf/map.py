#!/usr/bin/env python

import json
import os
import sys

from lib.fileutil import generated_path
from lib.calc.sf import units_per_density_limit, units_per_height, LOT_SIZE, NewZoneDetected
from lib.calc import color, key_stats

def main():

    with open(generated_path('sf/zoning_height.geojson')) as f:
        obj = json.load(f)

    new_zones = set()
    l = obj['features']
    for o in l:
        coords = o['geometry']['coordinates']
        prop = o['properties']

        try:
            homes_zoning = units_per_density_limit(prop['zoning'])
        except NewZoneDetected:
            new_zones.add(prop['zoning'])

        homes_height = units_per_height(prop['height_str'], prop['height'], prop['zoning'])
        homes = min(homes_zoning, homes_height)
        t = (homes_zoning, homes_height, homes, prop['height_str'])
        prop['homes'] = homes
        prop['homes_zoning'] = homes_zoning
        prop['homes_height'] = homes_height
        prop['fill'] = color(homes)

    if new_zones:
        print('New Zones: \n\t' + '\n\t'.join(new_zones))
        return -1

    stats = key_stats(l, lot_size=LOT_SIZE, all_area_denom=True)
    stats['city'] = 'San Francisco'
    stats['center'] = [-122.42936665634733, 37.75967613988033]
    stats['zoom'] = 11.75

    os.makedirs(generated_path('sf'), exist_ok=True)

    with open(generated_path('sf/key_data.json'), 'w') as f:
        json.dump(stats, f)

    with open(generated_path('sf/density_map.geojson'), 'w') as f:
        json.dump(obj, f)

    print('Illegal to build apartment building in %s%% of SF' % round(stats['apt_illegal_pct'], 1))
    print('Illegal to build building with > 5 units in %s%% of SF' % round(stats['apt5_illegal_pct'], 1))
    print('Illegal to build affordable housing in %s%% of SF land zoned for residential' %
          round(stats['affordable_illegal_resi_pct'], 1))
    print('Illegal to build affordable housing in %s%% of SF' % round(stats['affordable_illegal_pct'], 1))

if __name__ == '__main__':
    sys.exit(main())
