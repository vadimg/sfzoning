#!/bin/bash

python3 -m venv ENV
. ENV/bin/activate

pip install -r requirements.txt
./get_data.sh
