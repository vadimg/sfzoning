import ujson


def dump(filename, features):
    with open(filename, 'w') as f:
        ujson.dump(dict(type='FeatureCollection', features=features), f)


def load(filename):
    with open(filename) as f:
        obj = ujson.load(f)
    return obj['features']
