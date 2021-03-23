import sys

from shapely.geometry import shape

from lib.calc.sf import units_per_density_limit, units_per_height, address
from lib.calc import sq_ft
from lib.results import Results
from lib.fileutil import generated_path
from lib.fileutil import load, dump

from collections import defaultdict
from colorutils import Color


# in ft, how much taller should the building be than allowed to mark it as illegal
# NOTE: height is not super accurate because it was done via a lidar scan from a
# plane, so the buffer is bigger than what you might expect
HEIGHT_BUFFER = 5

# in sq ft, how much smaller should the lot size be than allowed to mark it as illegal
AREA_BUFFER = 10

# outer: https://vis4.net/palettes/#/4|s|c2343e,ffa9ff|ffffe0,ff005e,93003a|1|1
# inner: https://vis4.net/palettes/#/3|s|dc5d7a,f083bb|ffffe0,ff005e,93003a|1|1
COLORS = ['#c2343e', '#dc5d7a', '#e7709a', '#f083bb', '#ffa9ff']


def color(illegal_homes):
    if int(illegal_homes) >= len(COLORS):
        return COLORS[-1]
    return COLORS[int(illegal_homes) - 1]


def main():
    features = load(generated_path('sf/lot_building_zoning.geojson'))

    r = Results()
    r.num_buildings = len(features)
    r.num_units = 0
    r.num_illegal_buildings = 0
    r.num_illegal_homes = 0
    r.num_units_in_illegal_building = 0
    illegal_homes = []
    nozones = []
    illegals = defaultdict(int)
    for i, obj in enumerate(features):
        print(i + 1, '/', len(features))
        prop = obj['properties']
        zoning = prop.get('zoning')
        if not zoning:
            nozones.append(obj)
            continue

        units = int(prop['resunits'])
        r.num_units += units

        if i % 1000 == 0:
            print(prop)

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
        color = Color((0, 0, 0))

        if area + AREA_BUFFER < min_area:
            illegal_units = units
            reasons.append('lot too small')
            color += Color(hex='#ff4224')  # red

        if units > allowed_units_density:
            illegal_units = max(illegal_units, units - int(allowed_units_density))
            reasons.append('too dense')
            color += Color(hex='#7b91f8')  # blue


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
                illegal_units = max(illegal_units, units - allowed_units)
                reasons.append('buildings too tall')
                color += Color(hex='#67cb53')  # green

        if illegal_units > 0:
            illegals[units] += int(area)
            r.num_illegal_buildings += 1
            r.num_illegal_homes += illegal_units
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
                'fill': color.hex,
                'reasons': ', '.join(reasons),
                'year_built': int(prop.get('yrbuilt')) or 'unknown',
            }
            illegal_homes.append(obj)

    print(r.results())
    print(illegals)

    assert not nozones
    dump('generated/sf/illegal_homes.geojson', illegal_homes)


if __name__ == '__main__':
    sys.exit(main())
