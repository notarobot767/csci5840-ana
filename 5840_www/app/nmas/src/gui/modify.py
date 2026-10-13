#!/usr/bin/env python3

from pathlib import Path
import yaml

import dev.creds
import file_object


def update_device_from_yaml(hostname: str, raw_yaml_text: str):
    """
    Parses submitted YAML text and updates configuration and credential files.
    Accepts either {key: val} or {hostname: {key: val}}.
    """
    try:
        data = yaml.safe_load(raw_yaml_text)
    except yaml.YAMLError as exc:
        return False, f"YAML Syntax Error: {exc}"

    if not isinstance(data, dict):
        return False, "Data root must be key-value pairs (a dictionary/mapping)."

    # Unpack if the user submitted with the root device name wrapper
    if hostname in data and isinstance(data[hostname], dict):
        data = data[hostname]

    config_path = dev.creds.get_template_path()
    creds_path = dev.creds.get_cred_path()

    configs = file_object.read_file_yaml(config_path, default={}) or {}
    creds = file_object.read_file_yaml(creds_path, default={}) or {}

    cred_keys = {
        "hostname",
        "driver",
        "username",
        "password",
        "user",
        "pass",
        "secret",
        "host",
        "device_type",
    }

    new_config = {}
    new_creds = {}

    for k, v in data.items():
        if str(k).lower() in cred_keys:
            new_creds[k] = v
        else:
            new_config[k] = v

    configs[hostname] = new_config
    creds[hostname] = new_creds

    file_object.write_file_yaml(config_path, configs)
    file_object.write_file_yaml(creds_path, creds)

    return True, None

if __name__ == "__main__":
    main()