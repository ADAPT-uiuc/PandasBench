#!/bin/bash

sudo apt-get update
sudo apt install python3.10 python3-pip python3-venv pyenv -y
pyenv local 3.10.16

# It's now in pandas-dataset root
cd ../
python3 -m venv ds-env
source ds-env/bin/activate

pip install -r requirements.txt --no-cache-dir

wget https://uofi.box.com/shared/static/tipejtwr4khhyzl207uhcwjh2i7k9u8l -O PandasBench_data.zip
# This should create a directory named data
unzip PandasBench_data.zip

cd ./scripts/
./docker_data_setup.sh