#!/usr/bin/env python3

from pathlib import Path
from flask import request, has_request_context
from html import escape
import yaml
import io
import paramiko
import tempfile
import time
import re


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

def _execute_show_config(device, command):
    """Executes a show config command over an interactive SSH shell,

    waiting past 'Building configuration...' until the prompt returns.
    """
    _, creds = get_raw_device_data(device)
    if not creds:
        return False, f"Credentials for device '{device}' not found."

    host = str(creds.get("host", "")).strip().strip("[]")
    username = creds.get("username") or creds.get("user")
    password = creds.get("password") or creds.get("pass")

    if not host or not username:
        return False, f"Missing host IP or username for device '{device}'."

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=host,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
        )

        channel = ssh.invoke_shell(width=300, height=5000)
        time.sleep(1)

        # Flush initial login banners and prompt
        if channel.recv_ready():
            channel.recv(65535)

        # Disable paging and send command
        channel.send("terminal length 0\n")
        time.sleep(0.3)
        if channel.recv_ready():
            channel.recv(65535)

        channel.send(f"{command}\n")

        output = ""
        max_wait = 25  # Large running configs can take several seconds to generate
        start_time = time.time()

        # Regex matching typical network device CLI prompt endings: e.g. "r3#", "switch(config)#", "router>"
        prompt_pattern = re.compile(r"[\r\n][\w\.\-]+(?:\([^\)]+\))?[#>] *$")

        while time.time() - start_time < max_wait:
            if channel.recv_ready():
                chunk = channel.recv(65535).decode("utf-8", errors="replace")
                output += chunk

                # Check if we have received the config and hit the final device prompt
                # (or the standard Cisco/Arista 'end' marker at the end of configs)
                tail = output[-200:] if len(output) > 200 else output
                if ("\nend\r\n" in output or "\nend\n" in output) and prompt_pattern.search(tail):
                    break
                elif prompt_pattern.search(tail) and "Building configuration" in output:
                    # Some devices don't have 'end' explicitly, but returned to prompt after building
                    break

            time.sleep(0.3)

        if not output:
            return False, "Received empty response from device."

        # Parse out echoes, banners, and trailing prompts
        cleaned_lines = []
        capture = False

        for line in output.splitlines():
            line_str = line.strip("\r")

            # Ignore the command echo
            if command in line_str:
                capture = True
                continue

            # Skip the 'Building configuration...' informational line
            if "Building configuration..." in line_str:
                capture = True
                continue

            if capture:
                # Discard the trailing CLI prompt
                if prompt_pattern.search("\n" + line_str):
                    continue
                cleaned_lines.append(line_str)

        final_output = "\n".join(cleaned_lines).strip()
        return True, final_output or output

    except Exception as e:
        return False, f"SSH connection failed to {host}: {str(e)}"
    finally:
        ssh.close()


def get_device_startup_config(device):
    """Fetches 'show startup-config' from the device."""
    return _execute_show_config(device, "show startup-config")


def get_device_running_config(device):
    """Fetches 'show running-config' from the device."""
    return _execute_show_config(device, "show running-config")
        
def main():
    print(get_device_buttons(current_path="/device/view/r3"))

if __name__ == "__main__":
    main()