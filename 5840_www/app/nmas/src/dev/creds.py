#!/usr/bin/env python3

import file_object

def get_creds():
    cred_file = "secrets/device_creds.yaml"
    return file_object.read_file_yaml(cred_file)

def get_device_cred(device):
    cred =  get_creds()[device]
    if cred:
        return cred
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
    pass

if __name__ == "__main__":
    main()