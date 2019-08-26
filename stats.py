import json

from calc.sf import units_per_density_limit, units_per_height
from calc import color, key_stats

with open('generated/zoning_height.geojson') as f:
    obj = json.load(f)

l = obj['features']
for o in l:
    coords = o['geometry']['coordinates']
    prop = o['properties']
    homes_zoning = units_per_density_limit(prop['zoning'])
    homes_height = units_per_height(prop['height_str'], prop['height'], prop['zoning'])
    homes = min(homes_zoning, homes_height)
    t = (homes_zoning, homes_height, homes, prop['height_str'])
    prop['homes'] = homes
    prop['homes_zoning'] = homes_zoning
    prop['homes_height'] = homes_height
    prop['fill'] = color(homes)


stats = key_stats(l)

with open('generated/key_data.json', 'w') as f:
    json.dump(stats, f)

with open('generated/density_map.geojson', 'w') as f:
    json.dump(obj, f)

print('Illegal to build apartment building in %s%% of SF' % round(stats['apt_illegal_pct'], 1))
print('Illegal to build building with > 5 units in %s%% of SF' % round(stats['apt5_illegal_pct'], 1))
print('Illegal to build affordable housing in %s%% of SF land zoned for residential' %
      round(stats['affordable_illegal_resi_pct'], 1))
print('Illegal to build affordable housing in %s%% of SF' % round(stats['affordable_illegal_pct'], 1))

