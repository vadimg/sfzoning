# Install

## Prerequisites
* Python3
* `brew install geos`

## Steps

Run `./install.sh`

# Run

**Make sure you are in the virtualenv by running `. ENV/bin/activate`**

* `python zoning_height_map.py` to generate `generated/zoning_height.geojson`
* `python stats.py` to generate `generated/zoning_height.geojson`

# View Map

Run: `python -m http.server`

View the map at http://localhost:8000

# Warning

I started this project using python 2, and then started using python 3. Some of the code in this repo might not yet be converted to work with python 3.
