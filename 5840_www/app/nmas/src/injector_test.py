#!/usr/bin/env python3

import device_netmiko
import time

def shut(interface):
    return [
        f"interface {interface}",
        "shut"
    ]

def noshut(interface):
    return [
        f"interface {interface}",
        "no shut"
    ]

def int_brief():
    return "show ipv6 interface brief"

def down_device_r2():
    # link s2 to r2
    dev = "s2"
    print(device_netmiko.run_cmd_set(dev, shut("et1")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))

    time.sleep(10)

    # link s4 to r2
    dev = "s4"
    print(device_netmiko.run_cmd_set(dev, shut("et3")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))

def up_device_r2():
    # link s4 to r2
    dev = "s4"
    print(device_netmiko.run_cmd_set(dev, noshut("et3")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))

    time.sleep(10)

    # link s2 to r2
    dev = "s2"
    print(device_netmiko.run_cmd_set(dev, noshut("et1")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))

def down_device_r1():
    # link s1 to r1
    dev = "s1"

    route = "ipv6 route ::/0 et2 fe80::a8c1:abff:fe18:9ad"
    print(device_netmiko.run_cmd_set(dev, route))
    print(device_netmiko.run_cmd_set(dev, "sh ipv6 route static"))
    return True
    time.sleep(10)
    
    print(device_netmiko.run_cmd_set(dev, shut("et1")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))
    return True
    time.sleep(10)

    # link s3 to r1
    dev = "s3"
    print(device_netmiko.run_cmd_set(dev, shut("et3")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))

def up_device_r1():
    # link s4 to r2
    dev = "s4"

    print(device_netmiko.run_cmd_set(dev, noshut("et3")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))

    time.sleep(10)

    # link s2 to r2
    dev = "s1"
    print(device_netmiko.run_cmd_set(dev, noshut("et1")))
    print(device_netmiko.run_cmd_set(dev, int_brief()))

    route = "no ipv6 route ::/0 et2 fe80::a8c1:abff:fe18:9ad"
    print(device_netmiko.run_cmd_set(dev, route))
    print(device_netmiko.run_cmd_set(dev, "sh ipv6 route static"))

def test():
    dev = "s1"
    cmd = "show ipv6 int brief"
    print(device_netmiko.run_cmd_set(dev, cmd))

def main():
    #down_device_r2()
    #up_device_r2()

    #down_device_r1()
    up_device_r1()
    #test()

if __name__ == "__main__":
    main()