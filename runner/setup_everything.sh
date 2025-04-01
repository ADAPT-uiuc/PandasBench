#!/bin/bash

sudo apt-get update
sudo apt install python3.10 python3-pip python3.10-venv -y

# It's now in pandas-dataset root
cd ../
python3 -m venv ds-env
source ds-env/bin/activate

cd runner
pip install -r requirements.txt --no-cache-dir
# It's now in pandas-dataset root
cd ../

wget https://uofi.box.com/shared/static/dcnyw761chg8hh14vp13wyilrobk0qb3 -O PandasBench_data.zip
# This should create a directory named PandasBench_data
unzip PandasBench_data.zip


cp ./scripts/copier.sh ./PandasBench_data

cd PandasBench_data
./copier.sh ../notebooks
cd ../