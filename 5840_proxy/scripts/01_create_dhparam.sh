#!/bin/bash

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

mkdir -p ./secrets
openssl dhparam -dsaparam -out ./secrets/dhparam.pem 4096
chmod 444 ./secrets/dhparam.pem