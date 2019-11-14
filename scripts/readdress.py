from lib.fileutil import load, dump, generated_path, data_path
from lib.calc.sf import address

FILENAME = 'sf/lot_building_zoning.geojson'

lots = load(generated_path(FILENAME))
for lot in lots:
    prop = lot['properties']
    new_address = address(prop)
    print(prop['address'], '->', new_address)
    prop['address'] = new_address

dump(generated_path(FILENAME), lots)
