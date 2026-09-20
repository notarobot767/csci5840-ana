#!/bin/bash

# elastic template for logstash syslog

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

docker compose up -d

ELASTIC_PW=$(cat ./secrets/elastic.key)
PROXY_BRIDGE=172.31.255.255:9200

curl -u elastic:$ELASTIC_PW -X \
  POST "http://$PROXY_BRIDGE/_index_template/syslog-cisco-army" \
 -H "Content-Type: application/json" \
 -d @scripts/json/template_syslog_cisco.json
# create cisco template

curl -u elastic:$ELASTIC_PW -X \
  POST "http://$PROXY_BRIDGE/_index_template/syslog-nginx-army" \
  -H "Content-Type: application/json" \
  -d @scripts/json/template_syslog_nginx.json
# create nginx template

# curl -u elastic:$ELASTIC_PW -X GET "http://$PROXY_BRIDGE/_index_template/syslog-cisco-army?pretty"
# curl -u elastic:$ELASTIC_PW -X GET "http://$PROXY_BRIDGE/_index_template/syslog-nginx-army?pretty"
# view output of template