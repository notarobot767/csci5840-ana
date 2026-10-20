#!/usr/bin/env python3

from dev import connect, creds
import pytest
from napalm import get_network_driver
import random

def test_ping6():
    """ping all devices that exist"""
    for device in creds.get_devices():
        hostname = creds.get_hostname(device)
        ping = connect.ping6(hostname)
        assert ping is not None
        assert ping.returncode == 0

def test_ping6_nonexistent():
    """attempt to ping a nonexistent device"""
    hostname = "2600:bad:c0de::dead:beef"
    ping = connect.ping6(hostname)
    assert ping is not None
    assert ping.returncode == 1

def test_get_connection():
    """attempt to connect to each device that exists"""
    for device in creds.get_devices():
        conn = connect.get_connection(device)
        assert conn is not None
        if conn:
            facts = conn.get_facts()
            assert facts is not None
            assert isinstance(facts, dict)

def test_run_cmd():
    """attempt to run basic show command on random device"""
    device = creds.get_randon_device()
    if device:
        output = connect.run_cmd(device, "show version")
        assert output is not None
        assert isinstance(output, str)
        assert "Uptime" in output
    else:
        assert device is None
            
def test_run_cmd_nonexistent():
    pass

def main():
    pass

if __name__ == "__main__":
    main()