#! /usr/bin/bash
clear

# create virtual env
echo "Checking if venv exists"
if [ -d .venv ]; then
    echo "Folder Exists"
else
    echo "Creating virtual environments"
    python -m venv .venv
fi

# open venv
echo "Activate venv"
source .venv/bin/activate

# install dependancies
pip install -r requirements.txt

# run script
python main.py

# exit venv
deactivate

# # after execution remove venv
rm -r .venv