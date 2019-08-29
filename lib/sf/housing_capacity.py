from calc import color
from collections import defaultdict

from calc import METER_TO_FEET
from calc.sf import units_per_density_limit, units_per_height
from results import Results
from fileutil import load, dump


HOUSING_CAN_BE_HERE = [x.split(' = ')[0] for x in """
MIPS = Office (Management, Information, Professional Services)
MISSING DATA = missing data
MIXED = Mixed Uses (Without Residential)
MIXRES = Mixed Uses (With Residential)
PDR = Industrial (Production, Distribution, Repair)
RETAIL/ENT = Retail, Entertainment
RESIDENT = Residential
VACANT = Vacant
ROW = Right-of-Way
Right of Way = Right-of-way
""".strip().split('\n')]


def main():
    features = load('generated/lot_building_zoning.geojson')

    avail5 = []
    avail10 = []
    affordable = []

    r = Results()
    r.lots = r.avail = r.affarea = r.affunits = r.afflots = 0
    affordable_resunits = defaultdict(int)

    for i, obj in enumerate(features):
        print i + 1, '/', len(features)
        prop = obj['properties']
        zoning = prop.get('zoning')
        if not zoning:
            continue

        if prop['landuse'] == 'OpenSpace':
            continue

        units = int(prop['resunits'])
        area = prop['sqft']

        units_density = units_per_density_limit(zoning['zoning'], lot_size=area, per_lot_size=False)
        height = max(zoning['height'], 60)
        units_height = units_per_height(zoning['height_str'],
                                        height,
                                        zoning['zoning'],
                                        lot_size=area)

        if units_density <= 0 or units_height <= 0:
            continue

        # fractional units is not cool
        if units_height > 0:
            units_height = max(1, units_height)

        units_density = 1e9

        reg_units = min(units_density, units_height)

        avail = int(reg_units) - units

        avail_norm = avail * 2500.0 / max(area, 2500)
        if avail_norm <= 5:
            continue

        r.avail += avail
        r.lots += 1

        max_height = 0
        for building in prop.get('buildings', []):
            height_ft = METER_TO_FEET * float(building['properties']['hgt_mediancm']) / 100.0
            max_height = max(max_height, height_ft)
            print '\t', height_ft

        prop['fill'] = '#609e00'  # color(int(max_height / 10.0))
        prop['max_building_height'] = max_height
        prop['avail'] = avail
        prop['avail_norm'] = avail_norm
        prop['zcode'] = zoning['zoning']
        prop['hcode'] = zoning['height_str']
        if avail_norm > 5:
            avail5.append(obj)
        if avail_norm > 10:
            avail10.append(obj)

        if (area >= 10e3 and
                reg_units >= 50 and
                prop['landuse'] in HOUSING_CAN_BE_HERE):
            if units > 2:
                continue
            if prop['landuse'] != 'PDR' and max_height > 35:
                continue
            if max_height > 50:
                # no matter what ;)
                continue
            r.affarea += area
            print units_height, reg_units, area
            r.affunits += reg_units
            r.afflots += 1
            affordable.append(obj)
            affordable_resunits[units] += 1

    print r.results()
    for k in sorted(affordable_resunits):
        print k, affordable_resunits[k]

    dump('generated/avail5.geojson', avail5)
    dump('generated/avail10.geojson', avail10)
    dump('generated/affordable.geojson', affordable)


if __name__ == '__main__':
    main()
