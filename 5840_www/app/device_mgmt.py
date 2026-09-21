#!/usr/bin/env python3

from pathlib import Path
import yaml
from flask import request
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

def main():
    print(get_device_buttons(current_path="/device/view/r3"))

if __name__ == "__main__":
    main()