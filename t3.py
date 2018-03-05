import json

with open('res.geojson') as f:
    obj = json.load(f)

res = []
for i, o in enumerate(obj['features']):
    height = int(o['properties']['height'])
    height_str = o['properties']['height_str']
    zoning = o['properties']['zoning']
    if height > 1000 and height < 9999:
        res.append(o)
        print zoning, height_str

with open('debug.geojson', 'w') as f:
    json.dump(dict(type='FeatureCollection', features=res), f)
