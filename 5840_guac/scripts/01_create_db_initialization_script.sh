#!/bin/bash

# postgres needs an initial script to build the guacamole db
# the script can be pulled from the guac container, so we are doing that
# this script will be mounted to the postgres database and ran if the db is empty

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

mkdir -p ./app
# create app directory if it doesn't exist

echo creating 001-initdb.sql in app directory...
docker run --rm guacamole/guacamole:1.6.0 /opt/guacamole/bin/initdb.sh --postgresql > ./app/001-initdb.sql
# create the necessary database initialization script

ls -l ./app