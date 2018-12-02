from calc import color
from shapely.geometry import shape

from calc import units_per_density_limit, units_per_height
from results import Results
from fileutil import load, dump
from illegal_homes import sq_ft, address


def main():
    features = load('generated/building_zoning.geojson')

    avail5 = []
    avail10 = []
    r = Results()
    r.lots = r.avail = 0

    for i, obj in enumerate(features):
        print i + 1, '/', len(features)
        prop = obj['properties']
        zoning = prop.get('zoning')
        if not zoning:
            continue

        if prop['landuse'] == 'OpenSpace':
            continue

        units = int(prop['resunits'])

        s = shape(obj['geometry'])
        area = sq_ft(s)

        units_density = units_per_density_limit(zoning['zoning'], lot_size=area, per_lot_size=False)
        units_height = units_per_height(zoning['height_str'], zoning['height'], zoning['zoning'], lot_size=area)

        if units_density < 0 or units_height < 0:
            continue

        # fractional units is not cool
        if units_height > 0:
            units_height = max(1, units_height)

        reg_units = min(units_density, units_height)

        avail = int(reg_units) - units

        avail_norm = avail * 2500.0 / max(area, 2500)
        if avail_norm <= 5:
            continue

        r.avail += avail
        r.lots += 1

        prop['fill'] = color(avail_norm)
        prop['address'] = address(prop)
        prop['avail'] = avail
        prop['avail_norm'] = avail_norm
        prop['area'] = area
        prop['zcode'] = zoning['zoning']
        prop['hcode'] = zoning['height_str']
        if avail_norm > 5:
            avail5.append(obj)
        if avail_norm > 10:
            avail10.append(obj)

    print r.results()

    dump('generated/avail5.geojson', avail5)
    dump('generated/avail10.geojson', avail10)


if __name__ == '__main__':
    main()
