from dev import connect, creds
import pytest
from napalm import get_network_driver

def test_ping6():
    for device in creds.get_devices():
        hostname = creds.get_hostname(device)
        ping = connect.ping6(hostname)
        assert ping is not None
        assert ping.returncode == 0

def test_ping6_nonexistent():
    hostname = "2600:bad:c0de::dead:beef"
    ping = connect.ping6(hostname)
    assert ping is not None
    assert ping.returncode == 1

def test_get_connection():
    for device in creds.get_devices():
        conn = connect.get_connection(device)
        assert conn is not None
        if conn:
            facts = conn.get_facts()
            assert facts is not None
            assert isinstance(facts, dict)
            
def main():
    pass

if __name__ == "__main__":
    main()