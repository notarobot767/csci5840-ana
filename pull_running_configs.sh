#!/bin/bash

# Ensure output directory exists
mkdir -p running_configs

# Define Cisco and Arista nodes
CISCO_NODES=("r3" "r4")
ARISTA_NODES=("r1" "r2" "s1" "s2" "s3" "s4")

ALL_NODES=("${CISCO_NODES[@]}" "${ARISTA_NODES[@]}")

for node in "${ALL_NODES[@]}"; do
  echo "Backing up running-config from ${node}..."
  output_file="running_configs/${node}.cfg"

  if [[ " ${CISCO_NODES[*]} " =~ [[:space:]]${node}[[:space:]] ]]; then
    # Cisco IOS/IOS-XE serves running-config directly over SCP
    scp -O "${node}:running-config" "${output_file}"
  else
    # Arista EOS running-config is captured cleanly via SSH command
    ssh "${node}" "show running-config" > "${output_file}"
  fi

  # Verify file was created and is not empty
  if [[ -s "${output_file}" ]]; then
    echo "✓ Successfully saved ${output_file}"
  else
    echo "✗ Failed to pull running-config for ${node}" >&2
  fi
done