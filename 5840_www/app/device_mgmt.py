#!/usr/bin/env python3

from pathlib import Path
import yaml
from flask import request, has_request_context
from html import escape

def get_devices():
    config_path = Path("device_config.yaml")
    creds_path = Path("device_creds.yaml")

    configs = (
        yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    ) or {}
    creds = (
        yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}
    ) or {}

    devices = {}
    all_keys = set(configs.keys()) | set(creds.keys())

    for device in all_keys:
        # Merge all elements from both files for this device
        devices[device] = (
            configs.get(device, {}) | creds.get(device, {})
            if isinstance(configs.get(device), dict)
            and isinstance(creds.get(device), dict)
            else {**configs.get(device, {}), **creds.get(device, {})}
        )
    return devices

def get_device_list():
    return sorted(get_devices().keys())

def get_device_buttons(current_path=None):
    if current_path is None and has_request_context():
        current_path = request.path
    html = [
        '<div class="btn-group" role="group" aria-label="Device View Actions">'
    ]
    for device in get_device_list():
        url = f"/device/view/{device}"
        is_active = current_path == url
        active_class = " active" if is_active else ""
        aria_current = ' aria-current="page"' if is_active else ""
        html.append(
            f'    <a role="button" class="btn btn-outline-primary{active_class}"'
            f"{aria_current} "
            'data-bs-toggle="tooltip" data-bs-placement="top" '
            f'href="{url}" title="View {escape(device)}">\n'
            f"        {escape(device)}\n"
            "    </a>"
        )
    html.append("</div>\n<br><br>")
    return "\n".join(html)

def get_device_yaml(device):
    data = get_devices().get(device)
    if data is None:
        return ""

    # Sensitive keys to exclude (case-insensitive)
    sensitive_keys = {"user", "username", "password", "pass", "secret"}

    def sanitize(item):
        if isinstance(item, dict):
            return {
                k: sanitize(v)
                for k, v in item.items()
                if str(k).lower() not in sensitive_keys
            }
        elif isinstance(item, list):
            return [sanitize(elem) for elem in item]
        return item

    cleaned_data = sanitize(data)
    return yaml.dump({device: cleaned_data}, default_flow_style=False, sort_keys=False)

def add_device(hostname, ipv6_addr, vendor, template, username="cisco", password="cisco"):
    """
    Adds a device to device_config.yaml and device_creds.yaml if it doesn't already exist.
    Returns (True, None) on success or (False, "error message") on failure.
    """
    config_path = Path("device_config.yaml")
    creds_path = Path("device_creds.yaml")

    configs = (yaml.safe_load(config_path.read_text()) if config_path.exists() else {}) or {}
    creds = (yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}) or {}

    if hostname in configs or hostname in creds:
        return False, f"Device '{hostname}' already exists."

    # Update configs dict
    configs[hostname] = {
        "template": template
    }

    # Update creds dict
    creds[hostname] = {
        "host": ipv6_addr,
        "device_type": vendor,
        "username": username,
        "password": password
    }

    # Write back to files
    with open(config_path, "w") as f:
        yaml.safe_dump(configs, f, default_flow_style=False, sort_keys=False)

    with open(creds_path, "w") as f:
        yaml.safe_dump(creds, f, default_flow_style=False, sort_keys=False)

    return True, None

def remove_device(hostname):
    """
    Removes a device from device_config.yaml and device_creds.yaml.
    Returns (True, None) on success or (False, "error message") on failure.
    """
    config_path = Path("device_config.yaml")
    creds_path = Path("device_creds.yaml")

    configs = (yaml.safe_load(config_path.read_text()) if config_path.exists() else {}) or {}
    creds = (yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}) or {}

    if hostname not in configs and hostname not in creds:
        return False, f"Device '{hostname}' not found."

    configs.pop(hostname, None)
    creds.pop(hostname, None)

    with open(config_path, "w") as f:
        yaml.safe_dump(configs, f, default_flow_style=False, sort_keys=False)

    with open(creds_path, "w") as f:
        yaml.safe_dump(creds, f, default_flow_style=False, sort_keys=False)

    return True, None

def get_raw_device_data(hostname):
    """
    Returns separate (config_dict, creds_dict) for a specific device.
    """
    config_path = Path("device_config.yaml")
    creds_path = Path("device_creds.yaml")

    configs = (yaml.safe_load(config_path.read_text()) if config_path.exists() else {}) or {}
    creds = (yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}) or {}

    return configs.get(hostname, {}), creds.get(hostname, {})


def update_device(hostname, submitted_data):
    """
    Accepts a dictionary of key/value pairs for `hostname`.
    Splits keys appropriately between device_creds.yaml and device_config.yaml,
    parsing nested YAML/JSON strings where applicable.
    """
    config_path = Path("device_config.yaml")
    creds_path = Path("device_creds.yaml")

    configs = (yaml.safe_load(config_path.read_text()) if config_path.exists() else {}) or {}
    creds = (yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}) or {}

    cred_keys = {"host", "device_type", "username", "password", "user", "pass", "secret"}

    new_config = {}
    new_creds = {}

    for k, v in submitted_data.items():
        # Attempt to parse YAML/JSON in values (e.g. ints, dicts, booleans)
        if isinstance(v, str):
            v_stripped = v.strip()
            try:
                parsed_v = yaml.safe_load(v_stripped)
                # Keep plain strings if safe_load evaluates to something unexpected
                val = parsed_v if parsed_v is not None or v_stripped in ("null", "~", "") else v
            except Exception:
                val = v
        else:
            val = v

        if str(k).lower() in cred_keys:
            new_creds[k] = val
        else:
            new_config[k] = val

    configs[hostname] = new_config
    creds[hostname] = new_creds

    with open(config_path, "w") as f:
        yaml.safe_dump(configs, f, default_flow_style=False, sort_keys=False)

    with open(creds_path, "w") as f:
        yaml.safe_dump(creds, f, default_flow_style=False, sort_keys=False)

    return True, None

def update_device_from_yaml(hostname, raw_yaml_text):
    """
    Parses submitted YAML text and cleanly distributes keys between
    device_config.yaml and device_creds.yaml.
    """
    config_path = Path("device_config.yaml")
    creds_path = Path("device_creds.yaml")

    try:
        data = yaml.safe_load(raw_yaml_text)
    except yaml.YAMLError as e:
        return False, f"YAML Syntax Error: {str(e)}"

    if not isinstance(data, dict):
        return False, "Data root must be key-value pairs (a dictionary/mapping)."

    configs = (yaml.safe_load(config_path.read_text()) if config_path.exists() else {}) or {}
    creds = (yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}) or {}

    cred_keys = {"host", "device_type", "username", "password", "user", "pass", "secret"}

    new_config = {}
    new_creds = {}

    for k, v in data.items():
        if str(k).lower() in cred_keys:
            new_creds[k] = v
        else:
            new_config[k] = v

    configs[hostname] = new_config
    creds[hostname] = new_creds

    with open(config_path, "w") as f:
        yaml.safe_dump(configs, f, default_flow_style=False, sort_keys=False)

    with open(creds_path, "w") as f:
        yaml.safe_dump(creds, f, default_flow_style=False, sort_keys=False)

    return True, None

def get_device_raw_combined_yaml(device):
    """Returns the merged config + creds dictionary for editing without masking passwords."""
    cfg, cred = get_raw_device_data(device)
    merged = {**cfg, **cred}
    return yaml.dump(merged, default_flow_style=False, sort_keys=False)
    
def main():
    print(get_device_buttons(current_path="/device/view/r3"))

if __name__ == "__main__":
    main()