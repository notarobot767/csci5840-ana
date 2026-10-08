#!/usr/bin/env python3

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

import device.creds as creds
import file_object

def get_device_connection(device: str) -> ConnectHandler:
    """Establishes and returns an active Netmiko connection object."""
    cred = creds.get_device_cred(device)
    host = cred.get("host", device)

    try:
        # Do NOT use 'with' here, otherwise the connection closes on exit
        connection = ConnectHandler(**cred)
        return connection
    except NetmikoTimeoutException:
        print(f"Error: Connection timed out to {host}")
        return None
    except NetmikoAuthenticationException:
        print(f"Error: Authentication failed for {host}")
        return None
    except Exception as exc:
        print(f"Error connecting to {host}: {exc}")
        return None


def run_cmd(device: str, cmd: str, enable: bool = False) -> str:
    conn = get_device_connection(device)
    if conn is None:
        return f"Failed to run '{cmd}' because connection failed."
    try:
        if enable:
            conn.enable()
        return conn.send_command(cmd)
    finally:
        conn.disconnect()

def run_cmd_set(device: str, cmd_lst: list, enable: bool = True) -> str:
    conn = get_device_connection(device)
    if conn is None:
        return f"Failed to run '{cmd}' because connection failed."
    try:
        if enable:
            conn.enable()
        return conn.send_config_set(cmd_lst)
    finally:
        conn.disconnect()

def main():
    pass

if __name__ == "__main__":
    main()