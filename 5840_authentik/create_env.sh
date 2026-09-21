#!/bin/bash

# modified script from
# https://docs.goauthentik.io/docs/install-config/install/docker-compose

echo "AUTHENTIK_TAG=2025.2" > .env
echo >> .env
# recommend manually setting major version
# 2025.2 will pull latest minor 2025.2.1
# https://docs.goauthentik.io/docs/releases


echo "PG_PASS=$(openssl rand -base64 36 | tr -d '\n')" >> .env
echo "AUTHENTIK_SECRET_KEY=$(openssl rand -base64 60 | tr -d '\n')" >> .env