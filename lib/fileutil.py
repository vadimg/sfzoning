import os
import shapely
import ujson

BASE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


def data_path(filename):
    return os.path.join(BASE_DIR, 'data', filename)


def generated_path(filename):
    return os.path.join(BASE_DIR, 'generated', filename)


def dump(filename, features):
    with open(filename, 'w') as f:
        ujson.dump(dict(type='FeatureCollection', features=features), f)


def load(filename):
    with open(filename) as f:
        obj = ujson.load(f)
    return obj['features']


def poly2feature(polygon):
    return dict(
        type='Feature',
        properties={},
        geometry=shapely.geometry.geo.mapping(polygon),
    )
