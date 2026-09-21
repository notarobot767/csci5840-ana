#!/bin/bash

echo "TZ set as '$TZ'"
echo "setting timezone from TZ environment variable..."

ln -fs /usr/share/zoneinfo/$TZ /etc/localtime
dpkg-reconfigure -f noninteractive tzdata
# reconfigure timezone from TZ environment variable

ansible-playbook "$@"
# allows injection of args from compose.yaml in command field