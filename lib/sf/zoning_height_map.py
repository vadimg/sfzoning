#!/usr/bin/env python

import json
import os
from collections import namedtuple

from lib.fileutil import data_path, generated_path

from shapely.geometry import shape
import shapely

Zone = namedtuple('Zone', 'polygon zoning zoning_sim index')

with open(data_path('zoning.geojson')) as f:
    obj = json.load(f)
    print(obj['features'][0]['properties']['zoning'])

zones = []
for i, o in enumerate(obj['features']):
    zoning = o['properties']['zoning']
    zoning_sim = o['properties']['zoning_sim']
    zones.append(Zone(
        polygon=shape(o['geometry']),
        zoning=zoning,
        zoning_sim=zoning_sim,
        index=i))

with open(data_path('height.geojson')) as f:
    obj = json.load(f)
    print(obj['features'][100]['properties']['gen_hght'])

print('loaded')

Result = namedtuple('Result', 'polygon properties')
Intersect = namedtuple('Intersect', 'zoning area')

res = []
for i, o in enumerate(obj['features']):
    print(i, '/', len(obj['features']))
    height = int(o['properties']['gen_hght'])
    height_str = o['properties']['height']
    p = shape(o['geometry'])
    intersects = []
    for zone in zones:
        # fix self-intersecting polygons
        p = p.buffer(0)
        zp = zone.polygon.buffer(0)

        intersect = p.intersection(zp)
        if not intersect.is_empty:
            l = (list(intersect)
                 if intersect.geom_type == 'GeometryCollection'
                 else [intersect])
            for x in l:
                if x.area > 0:
                    res.append(Result(polygon=x,
                                      properties=dict(
                                          zoning=zone.zoning,
                                          zoning_sim=zone.zoning_sim,
                                          height=height,
                                          height_str=height_str,
                                          height_index=i,
                                          zone_index=zone.index,
                                      )))


obj = []
for r in res:
    obj.append(dict(
        type='Feature',
        properties=r.properties,
        geometry=shapely.geometry.geo.mapping(r.polygon),
    ))

os.makedirs(generated_path('sf'), exist_ok=True)

with open(generated_path('sf/zoning_height.geojson'), 'w') as f:
    json.dump(dict(type='FeatureCollection', features=obj), f)
