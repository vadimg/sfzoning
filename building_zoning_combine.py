import ujson
import sys


def main():
    num_splits = int(sys.argv[1])

    features = []
    for i in xrange(1, num_splits + 1):
        with open('generated/building_zoning-%d-of-%d.geojson' % (i, num_splits)) as f:
            obj = ujson.load(f)
        features.extend(obj['features'])

    with open('generated/building_zoning.geojson', 'w') as f:
        ujson.dump(dict(type='FeatureCollection', features=features), f)


if __name__ == '__main__':
    main()
