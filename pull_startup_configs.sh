#!/bin/bash

mkdir -p running_configs

# Define Cisco and Arista nodes
CISCO_NODES=("r3" "r4")
ARISTA_NODES=("r1" "r2" "s1" "s2" "s3" "s4")

ALL_NODES=("${CISCO_NODES[@]}" "${ARISTA_NODES[@]}")

for node in "${ALL_NODES[@]}"; do
  echo "--- Processing ${node} ---"

  # 1. Save active configuration to startup
  echo "Saving configuration on ${node}..."
  ssh "${node}" "write"

  # 2. Determine target path based on OS
  if [[ " ${CISCO_NODES[*]} " =~ [[:space:]]${node}[[:space:]] ]]; then
    # Cisco IOS/IOS-XE stores startup-config in NVRAM
    remote_path="startup-config"
  else
    # Arista EOS stores startup-config in flash
    remote_path="/mnt/flash/startup-config"
  fi

  # 3. Copy down the saved config
  echo "Downloading startup-config from ${node}..."
  scp -O "${node}:${remote_path}" "startup_configs/${node}.cfg"

  if [[ $? -eq 0 ]]; then
    echo "Successfully saved startup_configs/${node}.cfg"
  else
    echo "Failed to backup ${node}" >&2
  fi
done