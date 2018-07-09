import ujson

from shapely.geometry import shape

from results import Results
from calc import color
from illegal_homes import sq_ft
from fileutil import load, dump


def main():
    features = load('data/buildings.geojson')

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

    for obj in features:
        prop = obj['properties']
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

        prop['fill'] = color(units)
        if prop['landuse'] == 'OpenSpace':
            prop['fill'] = color(-1)
        all_homes.append(obj)

    print 'year built histogram', '-'*60
    for y in sorted(years.keys()):
        print y, ':', years[y]
    print '-'*80

    print r.results()

    dump('generated/single_family_homes.geojson', single_family)
    dump('generated/all_homes.geojson', all_homes)

if __name__ == '__main__':
    main()
