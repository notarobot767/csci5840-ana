#!/bin/bash

# create non reserved users for logstash and filebeat to write indexes

cd "$(dirname "$0")" || exit 1
# ensure script will always set working dir to script location

ELASTIC_PW=$(cat ../secrets/elastic.key)
LOGSTASH_WRITER_PW=$(cat ../secrets/logstash_writer.key)
FILEBEAT_WRITER_PW=$(cat ../secrets/filebeat_writer.key)
PROXY_BRIDGE=10.224.79.106:9200

##########
# logstash
##########
#curl -u elastic:$ELASTIC_PW -X DELETE "http://$PROXY_BRIDGE/_security/user/logstash_writer"
#curl -u elastic:$ELASTIC_PW -X DELETE "http://$PROXY_BRIDGE/_security/role/logstash_writer"
# delete if user/role exits

#curl -u elastic:$ELASTIC_PW -X \
#  POST "http://$PROXY_BRIDGE/_security/role/logstash_writer" \
#  -H "Content-Type: application/json" \
#  -d @json/logstash_writer_role.json
# create the logstash_writer role

#jq --arg pwd "$LOGSTASH_WRITER_PW" '. + {password: $pwd}' json/logstash_writer_user.json > ../secrets/logstash_writer_user.json
# recreate the user json file but with a password field in write to the secrets directory

#curl -u elastic:$ELASTIC_PW -X \
#  POST "http://$PROXY_BRIDGE/_security/user/logstash_writer" \
#  -H "Content-Type: application/json" \
#  -d @../secrets/logstash_writer_user.json
# create the logstash_writer user

#curl -u elastic:$ELASTIC_PW -X GET "http://$PROXY_BRIDGE/_security/role/logstash_writer?pretty"
#curl -u elastic:$ELASTIC_PW -X GET "http://$PROXY_BRIDGE/_security/user/logstash_writer?pretty"
# view the results of logstash user and role

##########
# filebeat
##########
#curl -u elastic:$ELASTIC_PW -X DELETE "http://$PROXY_BRIDGE/_security/role/filebeat_writer"
#curl -u elastic:$ELASTIC_PW -X DELETE "http://$PROXY_BRIDGE/_security/user/filebeat_writer"
# delete if user/role exists

curl -u elastic:$ELASTIC_PW -X \
  POST "http://$PROXY_BRIDGE/_security/role/filebeat_writer" \
  -H "Content-Type: application/json" \
  -d @json/filebeat_writer_role.json
# create the filebeat_writer role

jq --arg pwd "$FILEBEAT_WRITER_PW" '. + {password: $pwd}' json/filebeat_writer_user.json > ../secrets/filebeat_writer_user.json
# recreate the user json file but with a password field in write to the secrets directory

curl -u elastic:$ELASTIC_PW -X \
  POST "http://$PROXY_BRIDGE/_security/user/filebeat_writer" \
  -H "Content-Type: application/json" \
  -d @../secrets/filebeat_writer_user.json
# create the logstash_writer user

#curl -u elastic:$ELASTIC_PW -X GET "http://$PROXY_BRIDGE/_security/role/filebeat_writer?pretty"
#curl -u elastic:$ELASTIC_PW -X GET "http://$PROXY_BRIDGE/_security/user/filebeat_writer?pretty"
# view the results of filebeat user and role