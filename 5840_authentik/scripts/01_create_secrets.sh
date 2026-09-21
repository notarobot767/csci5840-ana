#!/bin/bash

# create user & pw for the postgres database
# this is for interaction between guacamole and postgres containers
# you should never use these credentials to login as a user

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

mkdir -p ./secrets
mkdir -p ./data
# create app directory if it doesn't exist

PG_USER=$(openssl rand -base64 60 | tr -dc 'A-Za-z' | head -c 20)
PG_PW=$(openssl rand -base64 64 | tr -dc 'A-Za-z0-9!@#$' | head -c 48)
AUTHENTIK_SECRET_KEY=$(openssl rand -base64 64 | tr -dc 'A-Za-z0-9!@#$' | head -c 48)

echo $PG_USER > ./secrets/db_user.key
echo $PG_PW > ./secrets/db_password.key
# postgres db


echo "AUTHENTIK_POSTGRESQL__USER=$PG_USER" > ./secrets/authentik.env
echo "AUTHENTIK_POSTGRESQL__PASSWORD=$PG_PW" >> ./secrets/authentik.env
echo "AUTHENTIK_SECRET_KEY=$AUTHENTIK_SECRET_KEY" >> ./secrets/authentik.env
# secrets for server and worker
# ideally would use docker secrets and point to a password file like above