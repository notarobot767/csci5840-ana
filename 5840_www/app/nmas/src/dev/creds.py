#!/usr/bin/env python3

import copy
import yaml
import file_object


def get_cred_path() -> str:
    return "secrets/device_creds.yaml"

def get_template_path() -> str:
    return "secrets/device_config.yaml"

def get_creds() -> dict:
    """Return dictionary of device credentials."""
    creds = file_object.read_file_yaml(get_cred_path(), default={})
    return creds if creds else {}

def get_template() -> dict:
    """Return dictionary of device configuration templates."""
    configs = file_object.read_file_yaml(get_template_path(), default={})
    return configs if configs else {}

def _sanitize(data: dict) -> dict:
    """Helper to remove sensitive keys like password."""
    sanitized = data.copy()
    sanitized.pop("password", None)
    return sanitized

def get_device_yaml(device: str, sanitize: bool = True) -> str | None:
    """Combine credentials and template configuration for a device and return as YAML."""
    creds = get_creds().get(device)
    config = get_template().get(device)

    if not creds and not config:
        return None

    device_data = {}
    if config:
        device_data.update(config)
    if creds:
        device_data.update(creds)

    if sanitize:
        device_data = _sanitize(device_data)

    return yaml.safe_dump(
        {device: device_data},
        default_flow_style=False,
        sort_keys=False,
    )

def get_device_cred(device: str) -> dict | None:
    creds = get_creds()
    return creds.get(device)

def get_devices() -> list[str]:
    creds = get_creds()
    if creds:
        return sorted(creds.keys())
    return []

def get_driver(device: str):
    dev_cred = get_device_cred(device)
    if dev_cred:
        return dev_cred.get("driver")
    return None

def get_hostname(device: str):
    dev_cred = get_device_cred(device)
    if dev_cred:
        return dev_cred.get("hostname")
    return None

def main():
    pass

if __name__ == "__main__":
    main()