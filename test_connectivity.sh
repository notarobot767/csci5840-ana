#!/usr/bin/env bash

# Destination targets (Webserver + all hosts)
declare -A TARGETS=(
  ["Webserver"]="2600:cafe:babe:f00d::10"
  ["clab-5840-h1"]="2600:bad:c0de:110:a8c1:abff:fed6:b7a2"
  ["clab-5840-h2"]="2600:bad:c0de:120:a8c1:abff:fe28:66ba"
  ["clab-5840-h3"]="2600:bad:c0de:210:a8c1:abff:fe8c:f06a"
  ["clab-5840-h4"]="2600:bad:c0de:230:a8c1:abff:fe1b:613d"
)

echo "============================================================"
echo " Starting Connectivity Tests from $(hostname)"
echo "============================================================"

for target_name in "${!TARGETS[@]}"; do
  target_ip="${TARGETS[$target_name]}"

  echo "############################################################"
  echo "# Testing Target: $target_name ($target_ip)"
  echo "############################################################"

  # 1. ICMPv6 Ping Test
  echo -e "\n[1] Ping Test -> ping -6 -c 1 -W 2 $target_ip"
  ping -6 -c 1 -W 2 "$target_ip" 2>&1 | grep -v -E '^---|packets transmitted|rtt'

  # 2. Curl Test (runs only against the Webserver)
  if [ "$target_name" == "Webserver" ]; then
    echo -e "\n[2] HTTP Test -> curl http://[$target_ip]"
    curl -sS "http://[$target_ip]"
    echo -e "\n"
  fi
done