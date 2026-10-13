#!/usr/bin/env python3

import dev.creds
import file_object


def get_vendors():
    return [
        ("ios", "Cisco IOS/IOS-XE"),
        ("iosxr", "Cisco IOS-XR"),
        ("nxos", "Cisco Nessus"),
        ("junos", "Juniper Junos"),
        ("eos", "Arista EOS")
    ]


def get_templates():
    return ["pe", "core", "access"]


def add_device(
    hostname,
    ipv6_addr,
    vendor,
    template,
    username="cisco",
    password="cisco",
):
    # Retrieve standardized file paths from creds module
    config_path = dev.creds.get_template_path()
    creds_path = dev.creds.get_cred_path()

    # Read existing configurations safely using default fallback
    configs = file_object.read_file_yaml(config_path, default={}) or {}
    creds = file_object.read_file_yaml(creds_path, default={}) or {}

    if hostname in configs or hostname in creds:
        return False, f"Device '{hostname}' already exists."

    # Update dictionaries
    configs[hostname] = {"template": template}
    creds[hostname] = {
        "hostname": ipv6_addr,
        "driver": vendor,
        "username": username,
        "password": password,
    }

    # Persist back to the respective paths
    file_object.write_file_yaml(config_path, configs)
    file_object.write_file_yaml(creds_path, creds)

    return True, None

def main():
    pass

if __name__ == "__main__":
    main()