import sys

from shapely.geometry import shape

from calc import units_per_density_limit, units_per_height, sq_ft, address
from results import Results
from fileutil import load, dump


def main():
    filename = sys.argv[1]

    features = load(filename)

    r = Results()
    r.num_buildings = len(features)
    r.num_units = 0
    r.num_illegal_buildings = 0
    r.num_illegal_homes = 0
    r.num_units_in_illegal_home = 0
    illegal_homes = []
    single_family = []
    nozones = []
    for i, obj in enumerate(features):
        print i + 1, '/', len(features)
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

        units_density = units_per_density_limit(zoning['zoning'], lot_size=area, per_lot_size=False)
        units_height = units_per_height(zoning['height_str'], zoning['height'], zoning['zoning'], area)

        if units_density < 0 or units_height < 0:
            continue

        # fractional units is not cool
        if units_height > 0:
            units_height = max(1, units_height)

        reg_units = min(units_density, units_height)

        if units == 1:
            single_family.append(obj)

        if units > reg_units:
            r.num_illegal_buildings += 1
            r.num_illegal_homes += units - int(reg_units)
            r.num_units_in_illegal_home += units
            obj['properties'] = {
                'address': address(prop),
                'units': units,
                'allowed_units': reg_units,
                'allowed_units_density': units_density,
                'allowed_units_height': units_height,
                'lot_sq_ft': area,
                'prop': obj['properties'],
            }
            illegal_homes.append(obj)

    print r.results()

    dump('generated/nozones.geojson', nozones)
    dump('generated/illegal_homes.geojson', illegal_homes)
    dump('generated/single_family_homes.geojson', single_family)


if __name__ == '__main__':
    main()
