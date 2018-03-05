import json

with open('data/height.geojson') as f:
    obj = json.load(f)
    print obj['features'][100]['properties']['gen_hght']

print 'loaded'

res = []
for i, o in enumerate(obj['features']):
    coords = o['geometry']['coordinates']
    height = int(o['properties']['gen_hght'])
    if height > 1000:
        print height, o['properties']['height']
