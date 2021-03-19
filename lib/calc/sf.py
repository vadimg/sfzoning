import math
import os
import yaml


with open(os.path.join(os.path.dirname(__file__), '../sf/zoning_density.yaml')) as f:
    lot_size_per_unit = yaml.safe_load(f)


LOT_SIZE = 2500.0
AVG_APT_SIZE = 800.0

GROUND_FLOOR_COMMERCIAL_REQUIRED_PREFIXES = (
    'NCT-',
    'C-3-',
)


class NewZoneDetected(Exception):
    pass


def units_per_density_limit(zone, lot_size=LOT_SIZE, per_lot_size=True):
    if '-OS' in zone:
        # a special open space zone
        return -1

    fixed = {
        'P': -1,  # parks are < 0
        'RH-1(D)': 2.0 * ((lot_size / 4000) if per_lot_size else 1),  # minimum lot size 4000 sq ft
        'RH-1': 2,
        'RH-1(S)': 2,
        'RH-2': 2,
        'RH-3': 3,
    }
    n = fixed.get(zone)
    if n is not None:
        return n

    lot_size_per = lot_size_per_unit.get(zone)
    if lot_size_per is None:
        raise NewZoneDetected(zone)

    if lot_size_per > 1e6:
        return 0
    if lot_size_per == 0:
        return 1e9
    return lot_size / lot_size_per


def units_per_height(height_code, height_num, zoning, lot_size=LOT_SIZE):
    if 'OS' in height_code:
        return -1

    sq_ft = lot_size * .8  # 80% efficiency

    apts_per_floor = sq_ft / AVG_APT_SIZE
    floors = math.floor(height_num / 10.0)

    for prefix in GROUND_FLOOR_COMMERCIAL_REQUIRED_PREFIXES:
        if zoning.startswith(prefix):
            floors -= 1
            break

    return apts_per_floor * floors


def address(prop):
    from_st = prop['from_st']
    to_st = prop['to_st']
    st_type = prop['st_type']

    if not st_type:
        st_type = ''

    number = from_st if from_st == to_st else '%s-%s' % (from_st, to_st)

    if not number or number == '0' or not prop['street'] or prop['street'] == 'UNKNOWN':
        return 'UNKNOWN'

    return '%s %s %s' % (number, prop['street'], st_type)
