# Install

## Prerequisites
* Python3
* `brew install geos`

## Steps

* Run `./install.sh`
* Run `./get_data.sh` (this will take awhile, it needs to download a lot of data)

# Run

* `make`

Or, for a specific city:
* `make sf`
* `make mountain_view`

# View Map

Run: `python3 -m http.server`

View the maps at:
* http://localhost:8000
* http://localhost:8000/#mountain_view

# Warning

I started this project using python 2, and then started using python 3. Some of the code in this repo might not yet be converted to work with python 3.
