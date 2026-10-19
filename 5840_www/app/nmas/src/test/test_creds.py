#!/usr/bin/env python3

from dev import creds
import pytest
import yaml

#####################
# Path & Helper Tests
#####################
def test_standard_paths():
    assert creds.get_cred_path() == "secrets/device_creds.yaml"
    assert creds.get_template_path() == "secrets/device_config.yaml"

def test_sanitize_removes_password_without_mutating_original():
    raw_data = {"username": "admin", "password": "supersecret", "driver": "ios"}
    cleaned = creds._sanitize(raw_data)

    assert "password" not in cleaned
    assert cleaned["username"] == "admin"
    assert "password" in raw_data  # Original dict remains untouched

#######
# creds
#######
def test_get_creds():
    cred = creds.get_creds()
    assert cred is not None
    assert isinstance(cred, dict)
    assert len(cred) > 0

def test_get_device_cred():
    """what to expect form an existing device"""
    cred = creds.get_device_cred("r1")
    assert cred is not None
    assert isinstance(cred, dict)
    for key in ["hostname", "driver", "username", "password"]:
        assert  key in cred

def test_get_device_cred_non_existent():
    """trying to pull a nonexistent device"""
    cred = creds.get_device_cred(creds.get_nonexistent_device())
    assert cred is None

def test_get_devices():
    devices = creds.get_devices()
    assert devices is not None
    assert isinstance(devices, list)

def test_get_driver():
    for device in creds.get_devices():
        driver = creds.get_driver(device)
        assert driver is not None
        assert isinstance(driver, str)
        assert driver in ["eos", "junos", "iosxr_netconf", "iosxr", "nxos", "nxos_ssh", "ios"]

def test_get_driver_nonexistent():
    driver = creds.get_driver(creds.get_nonexistent_device())
    assert driver is None

def test_get_hostname():
    for device in creds.get_devices():
        hostname = creds.get_hostname(device)
        assert hostname is not None
        assert isinstance(hostname, str)

def test_get_hostname_nonexistent():
    hostname = creds.get_hostname(creds.get_nonexistent_device())
    assert hostname is None

def main():
    pass

if __name__ == "__main__":
    main()