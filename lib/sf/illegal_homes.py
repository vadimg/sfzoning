import sys

from shapely.geometry import shape

from lib.calc.sf import units_per_density_limit, units_per_height, address
from lib.calc import sq_ft
from lib.results import Results
from lib.fileutil import load, dump


# in ft, how much taller should the building be than allowed to mark it as illegal
HEIGHT_BUFFER = 5

# in sq ft, how much smaller should the lot size be than allowed to mark it as illegal
AREA_BUFFER = 1

def color(illegal_homes):
    # https://vis4.net/palettes/#/10|s|c43e5f,ff9bff|ffffe0,ff005e,93003a|1|1
    COLORS = ['#c43e5f', '#cc496f', '#d45380', '#db5d91', '#e268a3', '#e872b5', '#ef7cc7', '#f486d9', '#fa91ec', '#ff9bff']
    if int(illegal_homes) >= len(COLORS):
        return COLORS[-1]
    return COLORS[int(illegal_homes)]


def main():
    filename = sys.argv[1]

    features = load(filename)

    r = Results()
    r.num_buildings = len(features)
    r.num_units = 0
    r.num_illegal_buildings = 0
    r.num_illegal_homes = 0
    r.num_units_in_illegal_building = 0
    illegal_homes = []
    nozones = []
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

        if area + AREA_BUFFER < min_area:
            illegal_units = units
            reasons.append('lot too small')

        if units > allowed_units_density:
            illegal_units = max(illegal_units, units - int(allowed_units_density))
            reasons.append('too dense')


        if max_median_height - HEIGHT_BUFFER > zoning['height']:
            illegal_units = max(illegal_units, units - int(units *
                                                           zoning['height'] /
                                                           max_median_height))
            reasons.append('buildings too tall')

        if illegal_units > 0:
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
                'fill': color(illegal_units),
                'reasons': ', '.join(reasons),
            }
            illegal_homes.append(obj)

    print(r.results())

    assert not nozones
    dump('generated/sf/illegal_homes.geojson', illegal_homes)


if __name__ == '__main__':
    sys.exit(main())
