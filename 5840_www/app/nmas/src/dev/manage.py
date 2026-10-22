#!/usr/bin/env python3

import file_object
from dev import connect, show, creds

def write_running_to_startup(device):
    """save running config to startup"""
    return connect.run_cmd(device, "write")

def write_startup_to_golden(device):
    """save startup config to golden"""
    if device:
        startup = show.get_startup(device)
        if startup:
            return file_object.write_file(creds.get_golden_path(device), startup)
    return False

def write_golden_to_startup(device):
    """overwrite startup config with current golden config"""
    if device:
        golden = show.get_golden(device)
        if golden:
            pass
            # tell router to copy from nmas or nams to router
    return False

def main():
    output = write_running_to_startup("r1")
    print(output)
    pass

if __name__ == "__main__":
    main()