#!/bin/bash

virtualenv ENV
. ENV/bin/activate

pip install -r requirements.txt
./get_data.sh
