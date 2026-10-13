#!/usr/bin/env python3

import dev.connect
import dev.creds
import file_object

from itertools import dropwhile
from pathlib import Path
import difflib
import re

def _get_dict_one_value(x: dict) -> str:
    return next(iter(x.values()))

def get_ospf_neighbors(device: str) -> str:
    if not device:
        return None
    driver = dev.creds.get_driver(device)
    if driver:
        match driver:
            case "ios":
                cmd = "show ospfv3 neighbor"
            case "eos":
                cmd = "show ipv6 ospf neighbor"
            case _:
                cmd = None
    if cmd:
        return dev.connect.run_cmd(device, cmd)
    return None

def get_bgp_neighbors(device: str) -> str:
    return dev.connect.run_cmd(device, "show bgp ipv6 unicast summary")

def get_route_table(device: str) -> str:
    return dev.connect.run_cmd(device, "show ipv6 route")

def get_device_cpu(device: str) -> str:
    if not device:
        return None
    driver = dev.creds.get_driver(device)
    if driver:
        match driver:
            case "ios":
                cmd = "show processes cpu sorted | exclude 0.00%"
            case "eos":
                cmd = "show processes top once | exclude 0.0"
            case _:
                cmd = None
    if cmd:
        return dev.connect.run_cmd(device, cmd)
    return None

def get_ping(device: str) -> str:
    if device:
        hostname = dev.creds.get_hostname(device)
        return dev.connect.ping6(hostname).stdout
    return None

def _get_config(device: str, config_type: str) -> str:
    if device and config_type:
        conn = dev.connect.get_connection(device)
        result = conn.get_config(config_type)
        conn.close()
        if result:
            return result[config_type].strip()
    return None

def get_running(device: str) -> str:
    return _get_config(device, "running")

def get_startup(device: str) -> str:
    return _get_config(device, "startup")

def get_golden(device):
    """Loads the golden configuration from /golden/<device>.cfg and strips leading/trailing newlines."""
    path = Path(f"/golden/{device}.cfg")
    return file_object.read_file(path).strip()

def sanitize_config(config: str) -> str:
    # 1. Strip PKI cert blocks first (avoids messing with line index loops)
    config = re.sub(
        r"crypto pki certificate chain[\s\S]*?\bquit\b",
        "",
        config,
        flags=re.IGNORECASE,
    )
    config = re.sub(
        r"certificate\s+(?:self-signed|ca)[\s\S]*?\bquit\b",
        "",
        config,
        flags=re.IGNORECASE,
    )

    # 2. Strip leading banners, blank lines, and initial '!' comments
    lines = config.splitlines()

    def should_drop(line: str) -> bool:
        stripped = line.replace("\xa0", " ").strip()
        if not stripped:
            return True
        if stripped.startswith("!"):
            return True
        if stripped.lower().startswith("using ") and "bytes" in stripped.lower():
            return True
        return False

    cleaned_lines = list(dropwhile(should_drop, lines))
    return "\n".join(cleaned_lines)

def build_side_by_side_diff(left_text, right_text, context_lines=1):
    """
    Generates compact context diff (changes + context lines) in side-by-side rows.
    Works for any two text/config inputs.
    """
    left_text = sanitize_config(left_text)
    right_text = sanitize_config(right_text)
    l_lines = left_text.splitlines() if left_text else []
    r_lines = right_text.splitlines() if right_text else []

    # If completely identical, return empty list
    if l_lines == r_lines:
        return []

    matcher = difflib.SequenceMatcher(None, l_lines, r_lines)
    groups = list(matcher.get_grouped_opcodes(n=context_lines))
    if not groups:
        return []

    rows = []
    for g_idx, group in enumerate(groups):
        if g_idx > 0:
            rows.append({
                "is_separator": True,
                "left_num": "...", "left_line": "...", "left_status": "separator",
                "right_num": "...", "right_line": "...", "right_status": "separator",
            })

        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                for idx, (l, r) in enumerate(zip(l_lines[i1:i2], r_lines[j1:j2])):
                    rows.append({
                        "is_separator": False,
                        "left_num": i1 + idx + 1, "left_line": l, "left_status": "equal",
                        "right_num": j1 + idx + 1, "right_line": r, "right_status": "equal",
                    })

            elif tag == "replace":
                count = max(i2 - i1, j2 - j1)
                for k in range(count):
                    has_l = (i1 + k) < i2
                    has_r = (j1 + k) < j2
                    rows.append({
                        "is_separator": False,
                        "left_num": (i1 + k + 1) if has_l else "",
                        "left_line": l_lines[i1 + k] if has_l else "",
                        "left_status": "replace" if has_l else "empty",
                        "right_num": (j1 + k + 1) if has_r else "",
                        "right_line": r_lines[j1 + k] if has_r else "",
                        "right_status": "replace" if has_r else "empty",
                    })

            elif tag == "delete":  # In left, missing on right
                for k in range(i2 - i1):
                    rows.append({
                        "is_separator": False,
                        "left_num": i1 + k + 1, "left_line": l_lines[i1 + k], "left_status": "delete",
                        "right_num": "", "right_line": "", "right_status": "empty",
                    })

            elif tag == "insert":  # Missing on left, added in right
                for k in range(j2 - j1):
                    rows.append({
                        "is_separator": False,
                        "left_num": "", "left_line": "", "left_status": "empty",
                        "right_num": j1 + k + 1, "right_line": r_lines[j1 + k], "right_status": "insert",
                    })
    return rows

def main():
    pass

if __name__ == "__main__":
    main()