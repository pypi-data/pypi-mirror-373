#!/usr/bin/env bash
set -e

export PYTHONPATH=$(pwd)  # this equals mlmanagement/client

python3 -m unittest discover -v -s $(pwd)/ML_management/tests/ -p 'test*.py'
