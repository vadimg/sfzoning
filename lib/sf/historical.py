import sys
import os
import re
from collections import defaultdict
from shapely.geometry import shape
import ujson as json

from lib.fileutil import load, dump, generated_path, data_path
from lib.calc.sf import units_per_density_limit, units_per_height, LOT_SIZE, NewZoneDetected
from lib.calc import color, key_stats, sq_ft

def parse_height(height_code):
    if height_code.startswith('OS'):
        return -1

    m = re.match(r'(\d+)', height_code)
    if not m:
        return
    return int(m.group(1))


UNKNOWN = '#ecd1ff'


def main():
    objs = load(data_path('zoning_height_2000.geojson'))

    new_zones = defaultdict(int)
    for i, o in enumerate(objs):
        prop = o['properties']

        zoning_code = prop['zoning']
        if zoning_code is None:
            prop['fill'] = UNKNOWN
            prop['homes'] = 0
            continue

        height_code = prop['height_lim']

        height = parse_height(height_code) if height_code is not None else None
        if height is not None:
            homes_height = units_per_height(height_code, height, zoning_code)
        else:
            homes_height = 1e9

        zoning_code = zoning_code.split('/')[0].strip()

        try:
            homes_zoning = units_per_density_limit(zoning_code,
                                                   waiverless_adus=False)
        except NewZoneDetected:
            s = shape(o['geometry'])
            area = sq_ft(s)
            new_zones[zoning_code] += area
            homes_zoning = 0
            print(prop)

        homes = min(homes_zoning, homes_height)
        prop['homes'] = homes
        prop['homes_zoning'] = homes_zoning
        prop['homes_height'] = homes_height
        prop['fill'] = color(homes) if homes_zoning != -999 else UNKNOWN

    stats = key_stats(objs, lot_size=LOT_SIZE, all_area_denom=True)
    stats['city'] = 'San Francisco'
    stats['center'] = [-122.42936665634733, 37.75967613988033]
    stats['zoom'] = 11.75

    os.makedirs(generated_path('sf2000'), exist_ok=True)
    dump('generated/sf2000/density_map.geojson', objs)

    with open(generated_path('sf2000/key_data.json'), 'w') as f:
        json.dump(stats, f)

    if new_zones:
        print('New Zones: \n\t' + '\n\t'.join(new_zones.keys()))
        print(new_zones)
        return -1

if __name__ == '__main__':
    sys.exit(main())
