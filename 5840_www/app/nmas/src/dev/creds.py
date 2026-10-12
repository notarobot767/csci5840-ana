#!/usr/bin/env python3

import file_object

def get_creds() -> dict:
    cred_file = "secrets/device_creds.yaml"
    creds = file_object.read_file_yaml(cred_file)
    if creds:
        return creds
    return None

def get_device_cred(device: str) -> dict:
    cred =  get_creds()[device]
    if cred:
        return cred
    return None

def get_devices() -> list[str]:
    devices = get_creds()
    if devices and len(devices) > 0:
        return sorted(get_creds().keys())
    return None

def get_driver(device: str):
    driver = get_device_cred(device).get("driver")
    if driver:
      return driver
    return None

def get_hostname(device: str):
    hostname = get_device_cred(device).get("hostname")
    if hostname:
      return hostname
    return None

def main():
    print(get_devices())

if __name__ == "__main__":
    main()