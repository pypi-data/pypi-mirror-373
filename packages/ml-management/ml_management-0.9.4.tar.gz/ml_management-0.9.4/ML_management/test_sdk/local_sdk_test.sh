#!/usr/bin/env bash
set -e

export PYTHONPATH=$(pwd)/mlmanagement/client/  # this equals mlmanagement/client

REGUSER=$1
REGPASS=$2

if [ -f $(pwd)/introspection/output/introspection.json ]; then
  echo 'Using existing introspection.json'
fi

# if introspection.json doesn't exist create it
if ! [ -f $(pwd)/introspection/output/introspection.json ]; then
  echo 'Generate introspection.'
  python3 -m venv introspection_venv
  source introspection_venv/bin/activate
  pip install --upgrade pip
  pip install --upgrade pip setuptools wheel
  pip install --no-cache-dir -r mlmanagement/server/requirements.txt --index-url https://$REGUSER:$REGPASS@nexus.intra.ispras.ru/repository/pypi-public/simple/
  pip install mlmanagement/client/
  sh local_introspect.sh
  deactivate
  rm -r introspection_venv
fi

NAME=test_sdk

# start docker container with nodeJS and python3 to mock_server
sudo docker run -d -v ${PWD}:/mlmanagement -p 4000:4000 --name $NAME nikolaik/python-nodejs:python3.10-nodejs18-slim sh -c "cd mlmanagement ; npm install --prefix mlmanagement/client/ML_management/test_sdk/ --no-save ; node mlmanagement/client/ML_management/test_sdk mock_server.js"

# run test_sdk.py
{
  python3 -m venv ${NAME}_env
  source ${NAME}_env/bin/activate
  pip install -r mlmanagement/client/ML_management/test_sdk/requirements.txt
  python3 -m unittest -v $(pwd)/mlmanagement/client/ML_management/test_sdk/test_sdk.py
} || {
    echo 'Test failed'
}

# stop and rm docker container
sudo docker stop $NAME

sudo docker rm $NAME

# rm created env
rm -r ${NAME}_env
