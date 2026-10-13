#!/usr/bin/env python3

import dev.creds
import file_object

def remove_device(hostname: str):
    config_path = dev.creds.get_template_path()
    creds_path = dev.creds.get_cred_path()

    configs = file_object.read_file_yaml(config_path, default={}) or {}
    creds = file_object.read_file_yaml(creds_path, default={}) or {}

    if hostname not in configs and hostname not in creds:
        return False, f"Device '{hostname}' not found."

    configs.pop(hostname, None)
    creds.pop(hostname, None)

    file_object.write_file_yaml(config_path, configs)
    file_object.write_file_yaml(creds_path, creds)

    return True, None

def main():
    pass

if __name__ == "__main__":
    main()