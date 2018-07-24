import math

ZONING = """
RH-1(D)	4000
RH-1	3000
RH-1(S)	1500
RH-2	1500
RH-3	1000
RM-1	800
RM-2	600
RM-3	400
RM-4	200
RC-3	400
RC-4	200
RCD	0
RTO	0
RTO-M	0
RH DTR	0
SB-DTR	0
TB DTR	0
WMUO	1.00E+09
WMUG	0
UMU	0
RED	0
RED-MX	0
MUO	0
MUG	0
MUR	0
SSO	200
NC-1	800
NC-2	800
NC-3	600
NC-S	800
NCD-POLK	400
NCD-UPPER FILLMORE	600
NCD-EXCELSIOR	600
NCD-WEST PORTAL	800
NCD-PACIFIC	1000
NCD-TARAVAL	800
NCD-SACRAMENTO	800
NCD-INNER CLEMENT	600
NCD-BROADWAY	400
NCD-HAIGHT	600
NCD-IRVING	800
NCD-CASTRO	600
NCD-UNION	600
NCD-INNER SUNSET	800
NCD-NORIEGA	800
NCD-NORTH BEACH	400
NCD-OUTER CLEMENT	600
NCD-JUDAH	800
NCD-UPPER MARKET	0
NCD-JAPANTOWN	400
NCD-24TH-NOE-VALLEY	600
NCT-FILLMORE	0
NCT-MISSION	0
NCT-HAYES	0
NCT-SOMA	0
NCT-OCEAN	0
NCT-UPPER MARKET	0
NCT-DIVISADERO	0
NCT-24TH-MISSION	0
NCT-GLEN PARK	0
NCT-FOLSOM	0
NCT-VALENCIA	0
NCT-1	0
NCT-2	0
NCT-3	0
C-2	800
C-3-G	125
C-3-O	125
C-3-O(SD)	125
C-3-R	125
C-3-S	125
M-1	1.00E+09
M-2	1.00E+09
PDR-1-B	1.00E+09
PDR-1-D	1.00E+09
PDR-1-G	1.00E+09
PDR-2	1.00E+09
SALI	1.00E+09
SLI	1.00E+09
CCB	200
CRNC	200
CVR	200
HP-RA	0
MB-O	1.00E+09
MB-OS	1.00E+09
MB-RA	0
PM-OS	1.00E+09
PM-S	1.00E+09
PM-CF	1.00E+09
PM-MU1	1.00E+09
PM-MU2	1.00E+09
PM-R	0
SPD	0
TI-MU	0
TI-R	0
TI-OS	1.00E+09
TI-PCI	1.00E+09
Job Corps	1.00E+09
YBI-MU	0
YBI-R	0
YBI-OS	1.00E+09
YBI-PCI	1.00E+09
MR-MU	0
P	1.00E+09
"""


lot_size_per_unit = {}
for l in ZONING.split('\n'):
    if l.strip():
        code, numstring = l.split('\t')
        lot_size_per_unit[code] = float(numstring)


LOT_SIZE = 2500.0
AVG_APT_SIZE = 800.0

GROUND_FLOOR_COMMERCIAL_REQUIRED_PREFIXES = (
    'NCT-',
    'C-',
)


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

    lot_size_per = lot_size_per_unit[zone]

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

COLORS = """
-1	gray
0	#3b0000
1	#950004
2	#c60003
3	#ff6e00
4	#ffbb00
5	#ffff00
6	#deec00
7	#bed900
10	#9ec500
12	#7eb100
15	#609e00
17	#428c00
20	#207700
22	#006400
"""

colors = {}
for l in COLORS.split('\n'):
    if l.strip():
        units, color = l.split('\t')
        colors[int(units)] = color


def color(units):
    units = int(units)
    if units > 20:
        return colors[max(colors.iterkeys())]

    while True:
        ret = colors.get(units)
        if ret is not None:
            return ret
        units -= 1
