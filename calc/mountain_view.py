ZONING = """
C-G	0	-1
C-I/RC	0	-1
C-N	0	-1
MU-1N	25	2
MU-2G	43	3
MU-3Cor	60	4
MU-4NBS	40	8
MU-5CtrNBS	40	15
MU-5CtrSA	70	8
MU-6D	119	8
OI-1	0	-1
OI-2	0	-1
OI-GI	0	-1
P-I	-1	-1
P-N	-1	-1
P-R	-1	-1
R-1LD	6	2
R-2MLD	12	2
R-3MD	25	2
R-4MHD	35	3
R-5HD	80	5
R-MBL	14	2
"""

code_data = {}
for l in ZONING.split('\n'):
    if l.strip():
        code, densitystr, heightstr = l.split('\t')
        code_data[code] = (float(densitystr), float(heightstr))


LOT_SIZE = 8000.0
SQ_FT_PER_ACRE = 43560.0
AVG_APT_SIZE = 800.0


def units_per_density_limit(zone):
    units_per_acre = code_data[zone][0]
    if units_per_acre <= 0:
        return units_per_acre

    return units_per_acre / SQ_FT_PER_ACRE * LOT_SIZE


def units_per_height(zone):
    if units_per_density_limit(zone) <= 0:
        return 0

    floors = code_data[zone][1]

    sq_ft = LOT_SIZE * .8  # 80% efficiency
    apts_per_floor = sq_ft / AVG_APT_SIZE

    return apts_per_floor * floors
