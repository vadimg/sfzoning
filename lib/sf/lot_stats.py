from shapely.geometry import shape

from results import Results
from calc import color
from illegal_homes import sq_ft, address
from fileutil import load, dump


def main():
    features = load('generated/lot_zoning.geojson')

    r = Results()
    r.units = 0
    r.units_sf = 0
    r.units_2_4 = 0
    r.units_5_9 = 0
    r.units_10_19 = 0
    r.units_20 = 0
    r.max_year = 0
    years = {}

    single_family = []
    all_homes = []
    homes_0_1 = []
    homes_2plus = []
    homes_3plus = []
    homes_5plus = []
    no_homes = []

    for i, obj in enumerate(features):
        print i, '/', len(features)

        prop = obj['properties']
        if prop.get('zoning') is None:
            continue

        units = int(prop['resunits'])
        year = int(prop['yrbuilt'])
        r.max_year = max(year, r.max_year)
        years.setdefault(year, 0)
        years[year] += units
        r.units += units
        if units == 1:
            r.units_sf += units
            single_family.append(obj)
        elif 2 <= units <= 4:
            r.units_2_4 += units
        elif 5 <= units <= 9:
            r.units_5_9 += units
        elif 10 <= units <= 19:
            r.units_10_19 += units
        elif units >= 20:
            r.units_20 += units

        s = shape(obj['geometry'])
        area = sq_ft(s)

        per_2500sqft = 2500.0 * float(units) / area

        prop['density_per_2500sqft'] = per_2500sqft
        prop['area'] = area

        if 0 < per_2500sqft < 1:
            per_2500sqft = 1

        per_2500sqft = int(per_2500sqft)

        prop['fill'] = color(per_2500sqft)
        prop['address'] = address(prop)
        if prop['landuse'] == 'OpenSpace':
            prop['fill'] = color(-1)
        elif 0 <= per_2500sqft <= 1:
            if per_2500sqft == 0:
                no_homes.append(obj)
            homes_0_1.append(obj)
        else:
            if per_2500sqft > 2:
                homes_3plus.append(obj)
            if per_2500sqft >= 5:
                homes_5plus.append(obj)
            homes_2plus.append(obj)
        all_homes.append(obj)

    print 'year built histogram', '-'*60
    for y in sorted(years.keys()):
        print y, ':', years[y]
    print '-'*80

    print r.results()

    dump('generated/single_family_homes.geojson', single_family)
    dump('generated/all_homes.geojson', all_homes)
    dump('generated/no_homes.geojson', no_homes)
    dump('generated/homes_0_1.geojson', homes_0_1)
    dump('generated/homes_2plus.geojson', homes_2plus)
    dump('generated/homes_3plus.geojson', homes_3plus)
    dump('generated/homes_5plus.geojson', homes_5plus)

    print len(homes_5plus)

if __name__ == '__main__':
    main()
