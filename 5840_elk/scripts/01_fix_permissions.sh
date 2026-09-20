#!/bin/sh

# create initial folder with user ownership
# otherwise root will be owner and cause issues

cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

# elastic
mkdir -p ./data/elastic
mkdir -p ./data/kibana
mkdir -p ./data/logstash
mkdir -p ./data/filebeat/netflow
mkdir -p ./secrets

chmod 600 ./app/filebeat/netflow.yml
chown -R $USER:$USER ./data
chown -R $USER:$USER ./secrets