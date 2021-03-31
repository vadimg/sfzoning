from shapely.geometry import shape

from lib.calc import METER_TO_FEET
from lib.fileutil import load, dump, generated_path, data_path
from lib.calc.sf import units_per_height, units_per_density_limit
from lib.polygon_index import PolygonIndex


def main():
    lots = load(generated_path('sf/lot_building_zoning.geojson'))

    new_lots = []
    too_tall = too_tall_nonwarehouse = 0

    for lot in lots:
        prop = lot['properties']
        zoning = prop['zoning']

        # must be a residential zone
        if prop['zoning']['homes'] <= 0:
            continue

        # cannot have any homes on it
        if float(prop['resunits']) > 0:
            continue

        # must be at least 10k sq ft
        if prop['sqft'] < 10e3:
            continue

        # affordable devs won't build taller than 85ft due to cost
        height = min(zoning['height'], 85)

        homes_zoning = units_per_density_limit(zoning['zoning'], lot_size=prop['sqft'])
        homes_height = units_per_height(
            zoning['height_str'],
            height,
            zoning['zoning'],
            lot_size=prop['sqft'])
        oldhomes = min(homes_zoning, homes_height)

        newhomes = units_per_height('', height, '', prop['sqft'])

        # affordable projects need at least 50 homes to get funding
        if newhomes < 50:
            continue

        # skip lots that could have built affordable housing already
        if oldhomes >= 50:
            continue

        # make it bright green
        prop['fill'] = '#7eb100'
        prop['opacity'] = 0.7

        max_height = 0
        for building in prop.get('buildings', []):
            height_ft = METER_TO_FEET * float(building['properties']['hgt_mediancm']) / 100.0
            max_height = max(max_height, height_ft)
            print('\t', height_ft)

        prop['max_building_height'] = max_height
        prop['oldhomes'] = oldhomes
        prop['newhomes'] = newhomes
        if 'buildings' in prop:
            del prop['buildings']

        CANNOT_DEMOLISH = {
            'fill': '#c60003',
            'opacity': 0.2,
        }

        # demolishing non-warehouse buildings taller than 35ft is too expensive
        if prop['landuse'] != 'PDR' and max_height > 35:
            too_tall_nonwarehouse += 1
            prop['infeasible_reason'] = (
                'demolishing non-warehouse buildings taller than 35ft is too expensive')
            prop.update(CANNOT_DEMOLISH)

        # demolishing buildings taller than 50ft is too expensive
        if max_height > 50:
            too_tall += 1
            prop['infeasible_reason'] = (
                'demolishing buildings taller than 50ft is too expensive')
            prop.update(CANNOT_DEMOLISH)

        new_lots.append(lot)

        print(newhomes, oldhomes, prop['sqft'], prop['zoning']['height'])

    print(len(new_lots), too_tall, too_tall_nonwarehouse)

    dump(generated_path('sf/prop_e.geojson'), new_lots)


if __name__ == '__main__':
    main()
