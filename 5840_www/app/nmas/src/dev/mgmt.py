#!/usr/bin/env python3

from html import escape
from pathlib import Path
from flask import has_request_context, request
import io
import json
import re
import secrets
import socket
import string
import subprocess
import time
import urllib.error
import paramiko
import yaml
import difflib

def update_device(hostname, submitted_data):
  config_path = Path("device_config.yaml")
  creds_path = Path("device_creds.yaml")

  configs = (
      yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
  ) or {}
  creds = (
      yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}
  ) or {}

  cred_keys = {
      "host",
      "device_type",
      "username",
      "password",
      "user",
      "pass",
      "secret",
  }
  new_config = {}
  new_creds = {}

  for k, v in submitted_data.items():
    if isinstance(v, str):
      v_stripped = v.strip()
      try:
        parsed_v = yaml.safe_load(v_stripped)
        val = (
            parsed_v
            if parsed_v is not None or v_stripped in ("null", "~", "")
            else v
        )
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
  config_path = Path("device_config.yaml")
  creds_path = Path("device_creds.yaml")

  try:
    data = yaml.safe_load(raw_yaml_text)
  except yaml.YAMLError as e:
    return False, f"YAML Syntax Error: {str(e)}"

  if not isinstance(data, dict):
    return False, "Data root must be key-value pairs (a dictionary/mapping)."

  configs = (
      yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
  ) or {}
  creds = (
      yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}
  ) or {}

  cred_keys = {
      "hostname",
      "driver",
      "username",
      "password",
      "user",
      "pass",
      "secret",
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

  with open(config_path, "w") as f:
    yaml.safe_dump(configs, f, default_flow_style=False, sort_keys=False)

  with open(creds_path, "w") as f:
    yaml.safe_dump(creds, f, default_flow_style=False, sort_keys=False)

  return True, None

# =====================================================================
# PASSWORD ROTATION & CREDS
# =====================================================================


def generate_device_password(length: int = 16) -> str:
  if length < 8:
    raise ValueError("Password length should be at least 8 characters.")

  cisco_safe_symbols = "!@#$%"
  uppercase = string.ascii_uppercase
  lowercase = string.ascii_lowercase
  digits = string.digits
  char_pool = uppercase + lowercase + digits + cisco_safe_symbols

  password = [
      secrets.choice(uppercase),
      secrets.choice(lowercase),
      secrets.choice(digits),
      secrets.choice(cisco_safe_symbols),
  ]
  password += [secrets.choice(char_pool) for _ in range(length - 4)]
  system_random = secrets.SystemRandom()
  system_random.shuffle(password)
  return "".join(password)


def _push_device_password_ssh(
    host, username, old_password, new_password, device_type="cisco_ios"
):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  try:
    clean_host = str(host).strip().strip("[]")
    ssh.connect(
        hostname=clean_host,
        username=username,
        password=old_password,
        look_for_keys=False,
        allow_agent=False,
        timeout=10,
    )

    channel = ssh.invoke_shell(width=300, height=5000)
    time.sleep(1.0)

    normalized_type = str(device_type).lower()
    if "arista" in normalized_type or "eos" in normalized_type:
      user_cmd = f"username {username} secret {new_password}\n"
    else:
      user_cmd = (
          f"username {username} algorithm-type sha256 secret {new_password}\n"
      )

    commands = [
        "terminal length 0\n",
        "configure terminal\n",
        user_cmd,
        "end\n",
        "write memory\n",
    ]

    output = ""
    for cmd in commands:
      channel.send(cmd)
      time.sleep(0.4)
      if channel.recv_ready():
        output += channel.recv(65535).decode("utf-8", errors="replace")

    time.sleep(0.8)
    if channel.recv_ready():
      output += channel.recv(65535).decode("utf-8", errors="replace")

    lower_out = output.lower()
    error_indicators = [
        "% invalid input",
        "% error",
        "% authorization failed",
        "% permission denied",
    ]
    if any(err in lower_out for err in error_indicators):
      return False, f"CLI error encountered: {output.strip()}"

    return True, None

  except Exception as e:
    return False, f"SSH operation failed: {str(e)}"
  finally:
    ssh.close()


def update_all_device_passwords(apply_to_devices: bool = True):
  creds_path = Path("device_creds.yaml")
  if not creds_path.exists():
    return False, "device_creds.yaml does not exist."

  creds = yaml.safe_load(creds_path.read_text()) or {}
  if not creds:
    return False, "device_creds.yaml is empty."

  report = {}
  for device_name, dev_info in creds.items():
    if not isinstance(dev_info, dict):
      report[device_name] = {
          "status": "skipped",
          "message": "Invalid device structure",
      }
      continue

    host = dev_info.get("host")
    username = dev_info.get("username") or dev_info.get("user")
    old_password = dev_info.get("password") or dev_info.get("pass")
    device_type = dev_info.get("device_type", "cisco_ios")

    if not host or not username or not old_password:
      report[device_name] = {
          "status": "failed",
          "message": "Missing host, username, or password",
      }
      continue

    new_password = generate_device_password(16)

    if apply_to_devices:
      success, err = _push_device_password_ssh(
          host=host,
          username=username,
          old_password=old_password,
          new_password=new_password,
          device_type=device_type,
      )
      if not success:
        report[device_name] = {
            "status": "failed",
            "message": f"Failed to push to device: {err}",
        }
        continue

    dev_info["password"] = new_password
    report[device_name] = {
        "status": "success",
        "message": f"Password rotated on {device_type} and YAML updated",
    }

  with open(creds_path, "w") as f:
    yaml.safe_dump(creds, f, default_flow_style=False, sort_keys=False)

  return True, report

def main():
  pass

if __name__ == "__main__":
  main()