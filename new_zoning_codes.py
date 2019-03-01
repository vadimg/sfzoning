import json
from calc import units_per_density_limit

with open('generated/zoning_height.geojson') as f:
    obj = json.load(f)

new_zones = set()

for o in obj['features']:
    prop = o['properties']
    try:
        units_per_density_limit(prop['zoning'])
    except Exception:
        new_zones.add(prop['zoning'])

print('\n'.join(new_zones))

