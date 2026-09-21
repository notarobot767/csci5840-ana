#!/bin/bash

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

mkdir -p ./secrets/self_signed

KEY_ALG=prime256v1
# list all ec curves
  # openssl ecparam -list_curves
# p-256, current popular standard for web keys. most compatible
# GCC requires 384 bits minimum for ecdsa
# other popular EC keys for web: prime256v1, secp384r1, secp521r1

ROOT_KEY=./secrets/self_signed/root.key.pem
ROOT_CERT=./secrets/self_signed/root.cert.pem
ROOT_CONF=./app/ext/root.conf
SERVER_KEY=./secrets/self_signed/key.pem
SERVER_CSR=./secrets/self_signed/csr.pem
SERVER_CERT=./secrets/self_signed/cert.pem
SERVER_CERT_CHAIN=./secrets/self_signed/cert-chain.pem
SERVER_CONF=./app/ext/self-signed-cert.conf
SERVER_CONF_EXT=./app/ext/self-signed-cert-ext.conf
DAYS=3652
  #10 years

# create root key
openssl ecparam -genkey -name $KEY_ALG -noout -out $ROOT_KEY
chmod 400 $ROOT_KEY

# create root cert
openssl req -x509 -new -days $DAYS -noenc \
  -key $ROOT_KEY -out $ROOT_CERT \
  -config $ROOT_CONF -extensions req_ext
chmod 444 $ROOT_CERT

# create server key
openssl ecparam -genkey -name $KEY_ALG -noout -out $SERVER_KEY
chmod 400 $SERVER_KEY

# create csr
openssl req -new -nodes \
  -key $SERVER_KEY -out $SERVER_CSR \
  -config $SERVER_CONF -extensions req_ext
chmod 444 $SERVER_CSR

# sign cert
openssl x509 -req -days $DAYS -sha512 -CAcreateserial \
  -in $SERVER_CSR -CA $ROOT_CERT -CAkey $ROOT_KEY \
  -out $SERVER_CERT -extfile $SERVER_CONF_EXT -extensions req_ext
chmod 444 $SERVER_CERT

# create certificate chain
cat $SERVER_CERT $ROOT_CERT > $SERVER_CERT_CHAIN
chmod 444 $SERVER_CERT_CHAIN

# print server cert chain
openssl x509 -text -noout -in $SERVER_CERT_CHAIN