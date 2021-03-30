import sys
import json

from shapely.geometry import shape

from lib.calc.sf import units_per_density_limit, units_per_height, address
from lib.calc import sq_ft
from lib.results import Results
from lib.fileutil import generated_path
from lib.fileutil import load, dump

from collections import defaultdict


# in ft, how much taller should the building be than allowed to mark it as illegal
# NOTE: height is not super accurate because it was done via a lidar scan from a
# plane, so the buffer is bigger than what you might expect
HEIGHT_BUFFER = 5

# in sq ft, how much smaller should the lot size be than allowed to mark it as illegal
AREA_BUFFER = 10

# https://vis4.net/palettes/#/5|s|e180e2,e43668|ffffe0,ff005e,93003a|1|1
COLORS = ['#e180e2', '#e56fc2', '#e75ea3', '#e64c85', '#e43668']


def color(illegal_homes):
    if int(illegal_homes) >= len(COLORS):
        return COLORS[-1]
    return COLORS[int(illegal_homes) - 1]


def main():
    features = load(generated_path('sf/lot_building_zoning.geojson'))

    r = Results()
    r.num_lots = len(features)
    r.num_units = 0
    r.num_illegal_lots = 0
    r.num_illegal_units = 0
    r.num_units_in_illegal_building = 0
    illegal_homes = []
    nozones = []
    illegals = defaultdict(int)
    reason_count = defaultdict(int)
    lot_sizez = {}
    for i, obj in enumerate(features):
        print(i + 1, '/', len(features))
        prop = obj['properties']
        zoning = prop.get('zoning')
        if not zoning:
            nozones.append(obj)
            continue

        units = int(prop['resunits'])
        r.num_units += units

        if units == 0:
            continue

        s = shape(obj['geometry'])
        area = sq_ft(s)

        min_area = 4000 if zoning['zoning'] == 'RH-1(D)' else 2500

        allowed_units_density = units_per_density_limit(zoning['zoning'], lot_size=area,
                                                per_lot_size=False,
                                                waiverless_adus=False)

        if allowed_units_density < 0:
            continue

        max_median_height = (max(float(b['properties']['hgt_mediancm']) for b in
                                prop['buildings']) / 30.48 if
                             prop.get('buildings') else 0)

        illegal_units = 0
        reasons = []

        if area + AREA_BUFFER < min_area:
            lot_sizez[area] = obj
            illegal_units = units
            reason_count['lot too small'] += units
            reasons.append('lot too small')

        if units > allowed_units_density:
            old_illegal_units = illegal_units
            illegal_units = max(illegal_units, units - int(allowed_units_density))
            reason_count['too dense'] += illegal_units - old_illegal_units
            reasons.append('too dense')

        if max_median_height - HEIGHT_BUFFER > zoning['height']:
            total_building_volume = sum((float(b['properties']['hgt_mediancm']) /
                                         30.48) *
                                        sq_ft(shape(b['geometry'])) for b in
                                        prop['buildings'])

            # calulate how many units each building would allow if its height
            # were chopped off at the zoning height (assuming even density of
            # units per building volume for each lot - definitely an incorrect
            # assumption but it's the best guess we can make)
            allowed_units = 0
            for b in prop['buildings']:
                building_height = float(b['properties']['hgt_mediancm']) / 30.48

                building_area = sq_ft(shape(b['geometry']))
                units_proportion = units * building_area * building_height / total_building_volume

                if building_height - HEIGHT_BUFFER > zoning['height']:
                    allowed_units += units_proportion * zoning['height'] / building_height
                else:
                    allowed_units += units_proportion

            allowed_units = int(round(allowed_units))
            if allowed_units < units:
                old_illegal_units = illegal_units
                illegal_units = max(illegal_units, units - allowed_units)
                reason_count['too tall'] += illegal_units - old_illegal_units
                reasons.append('too tall')

        if illegal_units > 0:
            illegals[color(illegal_units)] += illegal_units
            r.num_illegal_lots += 1
            r.num_illegal_units += illegal_units
            r.num_units_in_illegal_building += units

            obj['properties'] = {
                'address': address(prop),
                'units': units,
                'illegal_units': illegal_units,
                'allowed_units_density': allowed_units_density,
                'zoning_code': zoning['zoning'],
                'allowed_height': zoning['height'],
                'max_median_height': max_median_height,
                'lot_sq_ft': area,
                'minimum_lot_sq_ft': min_area,
                'fill': color(illegal_units),
                'reasons': ', '.join(reasons),
                'year_built': int(prop.get('yrbuilt')) or 'unknown',
            }
            illegal_homes.append(obj)

    print(r.results())

    key = []
    for i, c in enumerate(COLORS):
        key.append({
            'num': i + 1,
            'color': c,
        })

    key_data = {
        'key': key,
        'reason_counts': reason_count,
    }
    key_data.update(r.asdict())

    assert not nozones
    dump('generated/sf/illegal_homes.geojson', illegal_homes)

    with open(generated_path('sf/illegal_homes_key_data.json'), 'w') as f:
        json.dump(key_data, f)


if __name__ == '__main__':
    sys.exit(main())
