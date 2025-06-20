#!/bin/bash
# Create a virtual environment in the current directory
python3 -m venv venv

# Activate the virtual environment
source ./venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
if [ -f requirements_full.txt ]; then
    pip install -r requirements_full.txt
elif [ -f reqs.txt ]; then
    pip install -r reqs.txt
else
    echo "No requirements file found."
fi

echo "Virtual environment setup complete."
