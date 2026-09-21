#!/bin/bash

# create user & pw for the postgres database
# this is for interaction between guacamole and postgres containers
# you should never use these credentials to login as a user

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

mkdir -p ./secrets
# create app directory if it doesn't exist

echo creating random database user and password in secrets directory...
openssl rand -base64 32 | tr -dc 'A-Za-z' | head -c 32 > ./secrets/db_user.key
openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32 > ./secrets/db_password.key

ls -l ./secrets