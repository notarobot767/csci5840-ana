#!/bin/bash

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

mkdir -p ./secrets/server

KEY_ALG=secp384r1
# list all ec curves
  # openssl ecparam -list_curves
# p-256, current popular standard for web keys. most compatible
# GCC requires 384 bits minimum for ecdsa
# other popular EC keys for web: prime256v1, secp384r1, secp521r1

KEY=./secrets/server/key.pem
CSR=./secrets/server/csr.pem
CONF=./app/ext/server.conf

# create server key
openssl ecparam -genkey -name $KEY_ALG -noout -out $KEY
chmod 400 $KEY

# create csr
openssl req -new -nodes \
  -key $KEY -out $CSR \
  -config $CONF -extensions req_ext
chmod 444 $CSR

# print csr
openssl req -text -noout -verify -in $CSR

echo "output key to: $KEY"
echo "output csr to: $CSR"