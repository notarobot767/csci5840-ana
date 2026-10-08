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

ANSI_ESCAPE = re.compile(
    r"\x1B(?:\][^\x07\x1B]*?(?:\x07|\x1B\\)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_])"
)


def get_devices():
  config_path = Path("secrets/device_config.yaml")
  creds_path = Path("secrets/device_creds.yaml")

  configs = (
      yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
  ) or {}
  creds = (
      yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}
  ) or {}

  devices = {}
  all_keys = set(configs.keys()) | set(creds.keys())

  for device in all_keys:
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
  html = ['<div class="btn-group" role="group" aria-label="Device View Actions">']
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
  return yaml.dump(
      {device: cleaned_data}, default_flow_style=False, sort_keys=False
  )


def add_device(
    hostname,
    ipv6_addr,
    vendor,
    template,
    username="cisco",
    password="cisco",
):
  config_path = Path("device_config.yaml")
  creds_path = Path("device_creds.yaml")

  configs = (
      yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
  ) or {}
  creds = (
      yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}
  ) or {}

  if hostname in configs or hostname in creds:
    return False, f"Device '{hostname}' already exists."

  configs[hostname] = {"template": template}
  creds[hostname] = {
      "host": ipv6_addr,
      "device_type": vendor,
      "username": username,
      "password": password,
  }

  with open(config_path, "w") as f:
    yaml.safe_dump(configs, f, default_flow_style=False, sort_keys=False)

  with open(creds_path, "w") as f:
    yaml.safe_dump(creds, f, default_flow_style=False, sort_keys=False)

  return True, None


def remove_device(hostname):
  config_path = Path("device_config.yaml")
  creds_path = Path("device_creds.yaml")

  configs = (
      yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
  ) or {}
  creds = (
      yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}
  ) or {}

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
  config_path = Path("device_config.yaml")
  creds_path = Path("device_creds.yaml")

  configs = (
      yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
  ) or {}
  creds = (
      yaml.safe_load(creds_path.read_text()) if creds_path.exists() else {}
  ) or {}

  return configs.get(hostname, {}), creds.get(hostname, {})


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
  cfg, cred = get_raw_device_data(device)
  return yaml.dump({**cfg, **cred}, default_flow_style=False, sort_keys=False)


# =====================================================================
# SSH STREAM EXECUTION ENGINE
# =====================================================================


def _clean_stream(raw_text, command, device):
  """Cleans ANSI escapes, normalizes newlines, strips echo/banners/prompts,

  and stops cleanly at the terminal 'end' statement for configs.
  """
  sanitized = ANSI_ESCAPE.sub("", raw_text)
  sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")
  lines = sanitized.split("\n")

  cleaned = []
  echo_dropped = False
  cmd_stripped = command.strip()
  dev_lower = device.lower()
  is_config = any(w in command for w in ("running-config", "startup-config"))

  for line in lines:
    stripped = line.strip()
    stripped_lower = stripped.lower()

    # Drop only the first matching echo line
    if not echo_dropped and stripped == cmd_stripped:
      echo_dropped = True
      continue

    # Drop trailing prompt like r1# or switch-01#
    if (
        stripped_lower == f"{dev_lower}#"
        or stripped_lower == f"{dev_lower}>"
        or (
            (stripped_lower.startswith(dev_lower) or "#" in stripped_lower)
            and stripped_lower.endswith(("#", ">"))
        )
    ):
      continue

    # Drop AAA / syslog injected noise
    if "%ACCOUNTING-" in stripped or "%SYS-" in stripped:
      continue

    # Drop Cisco / Arista banner & byte metadata lines
    if stripped.startswith("Using ") and "bytes" in stripped:
      continue
    if stripped_lower == "building configuration...":
      continue
    if stripped.startswith("Current configuration : ") and stripped.endswith(
        "bytes"
    ):
      continue

    cleaned.append(line)

    # For running/startup configs, stop immediately on the final 'end'
    if is_config and stripped_lower == "end":
      break

  # Trim any lingering blank lines at the top or bottom
  while cleaned and not cleaned[0].strip():
    cleaned.pop(0)
  while cleaned and not cleaned[-1].strip():
    cleaned.pop()

  return "\n".join(cleaned)


def execute_show_command(device, command):
  """Executes command using interactive shell with accurate stream termination."""
  _, creds = get_raw_device_data(device)
  if not creds:
    return False, f"Credentials for device '{device}' not found."

  host = str(creds.get("host", "")).strip().strip("[]")
  username = creds.get("username") or creds.get("user")
  password = creds.get("password") or creds.get("pass")
  dev_type = str(creds.get("device_type", "")).lower()
  is_arista = (
      "arista" in dev_type or "eos" in dev_type or device.lower().startswith("s")
  )

  if not host or not username:
    return False, f"Missing host IP or username for device '{device}'."

  dev_lower = device.lower()
  is_config = any(w in command for w in ("running-config", "startup-config"))

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

    channel = ssh.invoke_shell(term="vt100", width=512, height=1000)

    # 1. Wait for initial prompt and set terminal parameters
    time.sleep(1.2)
    channel.send("terminal length 0\n")
    time.sleep(0.3)

    # Only Cisco supports 'terminal width 0'
    if not is_arista:
      channel.send("terminal width 0\n")
      time.sleep(0.3)

    # 2. Drain initial login banners and prompts completely
    while channel.recv_ready():
      channel.recv(65535)

    # 3. Format command - append | no-more on EOS to prevent --More-- paging stalls
    if is_arista and "| no-more" not in command:
      cmd_to_send = f"{command} | no-more\n"
    else:
      cmd_to_send = f"{command}\n"

    channel.send(cmd_to_send)

    # 4. Stream accumulator
    buf = ""
    start = time.time()
    max_timeout = 25.0 if is_config else 8.0
    last_recv_time = time.time()

    prompt_regex = re.compile(
        rf"(?:[\r\n]|^){re.escape(dev_lower)}(?:[\w\-\./\(\)]*)?[#>]\s*$",
        re.IGNORECASE,
    )

    while time.time() - start < max_timeout:
      if channel.recv_ready():
        chunk = channel.recv(65535).decode("utf-8", errors="replace")
        buf += chunk
        last_recv_time = time.time()
      else:
        time.sleep(0.05)
        # Check termination when output pauses for at least 0.35s
        if buf and (time.time() - last_recv_time > 0.35):
          norm = (
              ANSI_ESCAPE.sub("", buf)
              .replace("\r\n", "\n")
              .replace("\r", "\n")
              .rstrip()
          )

          # Verify if the prompt is sitting at the bottom of the output
          if prompt_regex.search(norm):
            if is_config:
              # For configs, confirm 'end' was already printed before the prompt
              if "\nend" in norm.lower():
                break
            else:
              break

    output = _clean_stream(buf, command, device)
    return True, output if output else "(No active entries found)"

  except Exception as e:
    return False, f"Connection failed to {host}: {str(e)}"
  finally:
    ssh.close()


def get_device_startup_config(device):
  """Fetches 'show startup-config'."""
  return execute_show_command(device, "show startup-config")


def get_device_running_config(device):
  """Fetches 'show running-config'."""
  return execute_show_command(device, "show running-config")


# =====================================================================
# OPERATIONAL SHOW COMMANDS (IPv6 ONLY)
# =====================================================================


def get_device_ospf_neighbors(device):
  """Fetches the OSPFv3 neighbor list for Cisco and Arista."""
  _, creds = get_raw_device_data(device)
  dev_type = str(creds.get("device_type", "")).lower()

  if "arista" in dev_type or "eos" in dev_type or device.lower().startswith("s"):
    # Arista EOS OSPFv3
    cmd = "show ipv6 ospf neighbor"
  else:
    # Cisco IOS OSPFv3 (detail shows full IPv6 link-local and interface info)
    cmd = "show ospfv3 neighbor"

  return execute_show_command(device, cmd)


def get_device_bgp_neighbors(device):
  """Fetches BGP IPv6 neighbor summary using standard syntax across both vendors."""
  # 'show bgp ipv6 unicast summary' is valid for both Cisco IOS and Arista EOS
  return execute_show_command(device, "show bgp ipv6 unicast summary")


def get_device_route_table(device):
  """Fetches IPv6 routing table."""
  return execute_show_command(device, "show ipv6 route")


def get_device_cpu(device):
  """Fetches CPU utilization safely for both Arista and Cisco."""
  _, creds = get_raw_device_data(device)
  dev_type = str(creds.get("device_type", "")).lower()

  if "arista" in dev_type or "eos" in dev_type or device.lower().startswith("s"):
    # show processes top once with | no-more prevents interactive curses blocking
    cmd = "show processes top once"
  else:
    cmd = "show processes cpu"

  return execute_show_command(device, cmd)


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


def ping_device(device, count=3, wait_timeout=1):
  """Pings the device IP address from the web server with a strict timeout."""
  _, creds = get_raw_device_data(device)
  if not creds:
    return False, f"Credentials/info for device '{device}' not found."

  host = str(creds.get("host", "")).strip().strip("[]")
  if not host:
    return False, f"Missing host address for device '{device}'."

  is_ipv6 = ":" in host
  cmd_candidates = [
      [
          "ping",
          "-6" if is_ipv6 else "-4",
          "-c",
          str(count),
          "-W",
          str(wait_timeout),
          host,
      ],
      [
          "ping6" if is_ipv6 else "ping",
          "-c",
          str(count),
          "-W",
          str(wait_timeout),
          host,
      ],
  ]

  max_exec_time = (count * wait_timeout) + 1

  last_error = None
  for cmd in cmd_candidates:
    try:
      proc = subprocess.run(
          cmd,
          stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT,
          text=True,
          timeout=max_exec_time,
      )
      return True, proc.stdout.strip()
    except subprocess.TimeoutExpired:
      return (
          False,
          f"Ping timed out after {max_exec_time}s. Host {host} is unreachable.",
      )
    except FileNotFoundError:
      last_error = "Ping executable not found on server system."
      continue
    except Exception as e:
      last_error = str(e)
      break

  return False, last_error or "Failed to execute ping."

def get_golden_config(device):
    """Loads the golden configuration from /golden/<device>.cfg and strips leading/trailing newlines."""
    golden_path = Path("/golden") / f"{device}.cfg"
    if not golden_path.exists():
        # Fallback to local ./golden/ directory if running in local dev
        alt_path = Path("golden") / f"{device}.cfg"
        if alt_path.exists():
            golden_path = alt_path
        else:
            return False, f"Golden config not found at /golden/{device}.cfg"
    try:
        content = golden_path.read_text(encoding="utf-8", errors="replace")
        # .strip() removes all leading and trailing whitespace, empty lines, and newlines (\r, \n)
        return True, content.strip()
    except Exception as e:
        return False, f"Failed reading golden config: {str(e)}"

def build_side_by_side_diff(golden_text, live_text, context_lines=2):
    """Generates standard compact context diff (changes + 2 context lines) in side-by-side rows."""
    g_lines = golden_text.splitlines()
    l_lines = live_text.splitlines()

    # Drop any leading blank lines from the live pull so it starts on the first real line/comment
    while l_lines and not l_lines[0].strip():
        l_lines.pop(0)

    matcher = difflib.SequenceMatcher(None, g_lines, l_lines)
    groups = list(matcher.get_grouped_opcodes(n=context_lines))
    if not groups:
        return []

    rows = []
    for g_idx, group in enumerate(groups):
        if g_idx > 0:
            rows.append({
                "is_separator": True,
                "g_num": "...", "g_line": "...", "g_class": "table-secondary text-muted",
                "l_num": "...", "l_line": "...", "l_class": "table-secondary text-muted",
            })
            
        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                for idx, (g, l) in enumerate(zip(g_lines[i1:i2], l_lines[j1:j2])):
                    rows.append({
                        "is_separator": False,
                        "g_num": i1 + idx + 1, "g_line": g, "g_class": "text-secondary",
                        "l_num": j1 + idx + 1, "l_line": l, "l_class": "text-secondary",
                    })
            elif tag == "replace":
                count = max(i2 - i1, j2 - j1)
                for k in range(count):
                    has_g = (i1 + k) < i2
                    has_l = (j1 + k) < j2
                    rows.append({
                        "is_separator": False,
                        "g_num": (i1 + k + 1) if has_g else "",
                        "g_line": g_lines[i1 + k] if has_g else "",
                        "g_class": "table-warning bg-warning bg-opacity-25" if has_g else "bg-light",
                        "l_num": (j1 + k + 1) if has_l else "",
                        "l_line": l_lines[j1 + k] if has_l else "",
                        "l_class": "table-warning bg-warning bg-opacity-25" if has_l else "bg-light",
                    })
            elif tag == "delete":  # In golden, missing on live device
                for k in range(i2 - i1):
                    rows.append({
                        "is_separator": False,
                        "g_num": i1 + k + 1, "g_line": g_lines[i1 + k],
                        "g_class": "table-danger bg-danger bg-opacity-25",
                        "l_num": "", "l_line": "", "l_class": "bg-light text-muted",
                    })
            elif tag == "insert":  # Added on live device
                for k in range(j2 - j1):
                    rows.append({
                        "is_separator": False,
                        "g_num": "", "g_line": "", "g_class": "bg-light text-muted",
                        "l_num": j1 + k + 1, "l_line": l_lines[j1 + k],
                        "l_class": "table-success bg-success bg-opacity-25",
                    })

    return rows

def main():
  print(update_all_device_passwords())


if __name__ == "__main__":
  main()