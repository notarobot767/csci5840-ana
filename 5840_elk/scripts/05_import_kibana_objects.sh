#!/bin/bash

# create kibana objects

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

docker compose up -d kibana

ELASTIC_PW=$(cat ./secrets/elastic.key)
PROXY_BRIDGE=172.31.255.255:6010

curl -X POST "http://172.31.255.255:6010/api/saved_objects/_import?overwrite=true" \
  -u elastic:$ELASTIC_PW \
  -H "kbn-xsrf: true" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@scripts/json/kibana_saved_objects.ndjson"

#curl -X GET "http://172.31.255.255:6010/api/saved_objects/_find?type=dashboard&per_page=100" \
#  -u elastic:$ELASTIC_PW \
#  -H "kbn-xsrf: true" \
#  -H "Content-Type: application/json" \
#  | jq
# basic GET request