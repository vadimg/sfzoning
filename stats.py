import json
from shapely.geometry import shape

from calc import units_per_2500sqft, units_per_height, color

with open('res.geojson') as f:
    obj = json.load(f)

mins = set()
s = {}
l = obj['features']
for o in l:
    coords = o['geometry']['coordinates']
    polygon = shape(o['geometry'])
    prop = o['properties']
    homes_zoning = units_per_2500sqft(prop['zoning'])
    homes_height = units_per_height(prop['height_str'], prop['height'])
    homes = min(homes_zoning, homes_height)
    mins.add(homes)
    t = (homes_zoning, homes_height, homes, prop['height_str'])
    prop['homes'] = homes
    prop['homes_zoning'] = homes_zoning
    prop['homes_height'] = homes_height
    prop['fill'] = color(homes)
    s.setdefault(t, 0)
    s[t] += polygon.area

all_area = sum(s.itervalues())

for tup, area in s.iteritems():
    l = list(tup) + [100.0*area/all_area]
    print ', '.join(map(str, l))

print '\n'.join(map(str, sorted(mins)))

with open('res2.geojson', 'w') as f:
    json.dump(obj, f)
