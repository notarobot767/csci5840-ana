#!/usr/bin/env python3
import json
import xmltodict
from ncclient import manager
from concurrent.futures import ThreadPoolExecutor

# Define your inventory
DEVICES = [
    {
        "host": "2600:BAD:C0DE::3",
        "name": "r3",
        "platform": "iosxe",
        "user": "cisco",
        "password": "password",
        "port": 830
    },
    {
        "host": "2600:bad:c0de::1",
        "name": "r1",
        "platform": "default",   # Arista uses the RFC-standard 'default' handler
        "user": "cisco",
        "password": "password",
        "port": 830
    }
]

# Both Cisco and Arista support the standard ietf-interfaces model
FILTER = """
<interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
"""

def poll_device(dev):
    results = []
    try:
        with manager.connect(
            host=dev["host"],
            port=dev["port"],
            username=dev["user"],
            password=dev["password"],
            hostkey_verify=False,
            timeout=20,
            device_params={'name': dev["platform"]}
        ) as m:
            reply = m.get(filter=('subtree', FILTER))
            data = xmltodict.parse(reply.xml)

            interfaces = data.get('rpc-reply', {}).get('data', {}).get('interfaces-state', {}).get('interface', [])
            if isinstance(interfaces, dict):
                interfaces = [interfaces]

            for intf in interfaces:
                stats = intf.get('statistics', {})
                results.append({
                    "device": dev["name"],
                    "host": dev["host"],
                    "interface": intf.get('name'),
                    "admin_status": intf.get('admin-status', 'unknown'),
                    "oper_status": intf.get('oper-status', 'unknown'),
                    "in_octets": int(stats.get('in-octets', 0)),
                    "out_octets": int(stats.get('out-octets', 0)),
                    "in_errors": int(stats.get('in-errors', 0)),
                    "out_errors": int(stats.get('out-errors', 0))
                })
    except Exception:
        pass
    return results

def main():
    # Poll concurrently so one slow node does not delay the cycle
    with ThreadPoolExecutor(max_workers=5) as executor:
        all_results = executor.map(poll_device, DEVICES)

    for dev_results in all_results:
        for metric in dev_results:
            print(json.dumps(metric))

if __name__ == "__main__":
    main()