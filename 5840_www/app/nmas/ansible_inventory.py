#!/usr/bin/env python3

import json
import sys
import dev.creds

# Map your NAPALM drivers to Ansible network OS / connection plugins
DRIVER_TO_NETWORK_OS = {
    "ios": "cisco.ios.ios",
    "eos": "arista.eos.eos",
    "junos": "junipernetworks.junos.junos",
    "nxos": "cisco.nxos.nxos",
    "iosxr": "cisco.iosxr.iosxr",
}

def build_inventory():
    creds = dev.creds.get_creds()
    configs = dev.creds.get_template()

    inventory = {
        "_meta": {"hostvars": {}},
        "all": {"hosts": []},
        # Group automatically by template (pe, core, access, ce)
    }

    for device_name, cred_info in creds.items():
        inventory["all"]["hosts"].append(device_name)

        driver = cred_info.get("driver", "ios")
        template = configs.get(device_name, {}).get("template", "default")

        # Group by template role
        if template not in inventory:
            inventory[template] = {"hosts": []}
        inventory[template]["hosts"].append(device_name)

        # Merge device vars from device_config.yaml
        dev_vars = configs.get(device_name, {}).copy()

        # Add Ansible connection and authentication variables
        dev_vars.update({
            "ansible_host": cred_info.get("hostname"),
            "ansible_user": cred_info.get("username"),
            "ansible_password": cred_info.get("password"),
            "ansible_network_os": DRIVER_TO_NETWORK_OS.get(driver, "cisco.ios.ios"),
            "ansible_connection": "network_cli",
            # If using napalm-ansible collection:
            "napalm_platform": driver,
        })

        inventory["_meta"]["hostvars"][device_name] = dev_vars

    return inventory

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(build_inventory(), indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        dev_name = sys.argv[2]
        inv = build_inventory()
        print(json.dumps(inv["_meta"]["hostvars"].get(dev_name, {})))
    else:
        print(json.dumps(build_inventory(), indent=2))

if __name__ == "__main__":
    main()