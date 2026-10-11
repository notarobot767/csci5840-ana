#!/usr/bin/env python3

import dev.connect
import dev.creds

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
    return dev.connect.run_cmd(
        device, "show bgp ipv6 unicast summary"
    ).strip()

def get_route_table(device: str) -> str:
    return dev.connect.run_cmd(
        device, "show ipv6 route"
    ).strip()

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

def _get_config(device: str, type: str) -> str:
    if device and type:
        conn = dev.connect.get_connection(device)
        result = conn.get_config(type)
        conn.close()
        if result:
            return result[type].strip()
    return None

def get_running(device: str) -> str:
    return _get_config(device, "running")

def get_startup(device: str) -> str:
    return _get_config(device, "startup")

def main():
    pass

if __name__ == "__main__":
    main()