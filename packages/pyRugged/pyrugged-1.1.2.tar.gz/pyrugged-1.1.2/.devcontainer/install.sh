#!/bin/sh -ex
python3.11 -m venv .venv
# Activate virtual Python environment
. .venv/bin/activate
# Upgrade pip, add support for Dependency Groups (PEP 735), since 25.1.
python -m pip install --upgrade pip
# Set Orekit-JCC pypi location
export PIP_INDEX_URL="https://gitlab.eopf.copernicus.eu/api/v4/projects/94/packages/pypi/simple"
# Install in editable mode
python -m pip install -e .
# Install dev dependencies
python -m pip install --group dev
