#!/bin/bash

# create elastic built-in system account passwords
# careful not to overwrite existing secrets

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

docker compose down 2> /dev/null
# containers should be stopped if changing credential info

####################
# kibana system user
####################
echo "xpack.reporting.encryptionKey: $(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)" > ./secrets/kibana.env
echo "ELASTICSEARCH_USERNAME: kibana_system" >> ./secrets/kibana.env
printf "ELASTICSEARCH_PASSWORD: " >> ./secrets/kibana.env
# reserved kibana user for system
# prepare kibana env file

########################################
# logstash system & logstash writer user
########################################
echo "LOGSTASH_WRITER_USER: logstash_writer" > ./secrets/logstash.env
printf "LOGSTASH_WRITER_PW: " >> ./secrets/logstash.env
LOGSTASH_WRITER_PW=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)
echo $LOGSTASH_WRITER_PW > ./secrets/logstash_writer.key
echo $LOGSTASH_WRITER_PW >> ./secrets/logstash.env
# custom user logstash needs to write indexes

echo "xpack.monitoring.elasticsearch.username: logstash_system" >> ./secrets/logstash.env
printf "xpack.monitoring.elasticsearch.password: " >> ./secrets/logstash.env
# reserved logstash user for system
# prepare logstash env file

######################
# filebeat writer user
######################
echo "FILEBEAT_USER: filebeat_writer" > ./secrets/fb_netflow.env
printf "FILEBEAT_PW: " >> ./secrets/fb_netflow.env
FILEBEAT_PW=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9!@#$%^&*()-_=+' | head -c 32)
echo $FILEBEAT_PW > ./secrets/filebeat_writer.key
echo $FILEBEAT_PW >> ./secrets/fb_netflow.env
# create filebeat secrets


#######################################################
# create elastic, kibana, and logstash system passwords
#######################################################
docker compose up -d elasticsearch
sleep 15
# ensure elastic is running
# give it enough time to start before sending commands

docker compose exec elasticsearch ./bin/elasticsearch-reset-password -u elastic -b -s > ./secrets/elastic.key
docker compose exec elasticsearch ./bin/elasticsearch-reset-password -u kibana_system -b -s >> ./secrets/kibana.env
docker compose exec elasticsearch ./bin/elasticsearch-reset-password -u logstash_system -b -s >> ./secrets/logstash.env
# write elastic key add kibana and logstash pw to their specific .env file
# https://www.elastic.co/guide/en/elasticsearch/reference/current/reset-password.html

docker compose up -d --force-recreate kibana
# rebuild the containers