import json
from shapely.geometry import shape

from calc import units_per_density_limit, units_per_height, color

with open('generated/res.geojson') as f:
    obj = json.load(f)

home_areas = {}
l = obj['features']
for o in l:
    coords = o['geometry']['coordinates']
    polygon = shape(o['geometry'])
    prop = o['properties']
    homes_zoning = units_per_density_limit(prop['zoning'])
    homes_height = units_per_height(prop['height_str'], prop['height'])
    homes = min(homes_zoning, homes_height)
    t = (homes_zoning, homes_height, homes, prop['height_str'])
    prop['homes'] = homes
    prop['homes_zoning'] = homes_zoning
    prop['homes_height'] = homes_height
    prop['fill'] = color(homes)
    home_areas.setdefault(homes, 0)
    home_areas[homes] += polygon.area

all_area = sum(home_areas.itervalues())

apt_illegal_pct = 0
apt5_illegal_pct = 0
dat = []
for m in sorted(home_areas.keys()):
    percentage = 100.0 * home_areas[m] / all_area
    dat.append({
        "homes": m,
        "percentage": percentage,
        "color": color(m),
    })

    if m <= 2:
        apt_illegal_pct += percentage
    if m <= 5:
        apt5_illegal_pct += percentage

    if m > 20:
        # the rest will be labeled "> 20"
        break

total_percent = sum(x['percentage'] for x in dat)
dat[-1]['percentage'] = 100 - total_percent

print json.dumps(dat, indent=2)

with open('generated/res2.geojson', 'w') as f:
    json.dump(obj, f)

print 'Illegal to build apartment building in %s%% of SF' % round(apt_illegal_pct, 1)
print 'Illegal to build building with > 5 units in %s%% of SF' % round(apt5_illegal_pct, 1)
