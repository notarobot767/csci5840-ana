#!/usr/bin/env python3

from dev import show, creds, connect
import pytest

def _device(device: str) -> str | None:
    if device in creds.get_devices():
        return device
    return None
####
# r1
####
def _device_r1():
    return _device("r1")

def test_state_r1_facts():
    facts = connect.get_facts(_device_r1())
    assert facts is not None
    if facts:
        assert facts["hostname"] == _device_r1()
        assert facts["vendor"] == "Arista"

def test_state_r1_loop0():
    output = connect.run_cmd(_device_r1(), "show ipv6 interface Loopback0 brief | include 2600:")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:bad:c0de::1/128" in output

def test_state_r1_ospf_neighbors():
    output = show.get_ospf_neighbors(_device_r1())
    assert output is not None and isinstance(output, str)
    assert "Neighbor 3.3.3.1 VRF default" in output

def test_state_r1_isis_neighbors():
    output = show.get_isis_neighbors(_device_r1())
    assert output is not None and isinstance(output, str)
    assert "CORE      default  s1               L2   Ethernet2" in output

def test_state_r1_config_drift():
    running = show.get_running(_device_r1())
    startup = show.get_startup(_device_r1())
    golden = show.get_golden(_device_r1())
    assert running is not None
    assert startup is not None
    assert golden is not None
    assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

####
# r2
####
def _device_r2():
    return _device("r2")

def test_state_r2_facts():
    facts = connect.get_facts(_device_r2())
    assert facts is not None and isinstance(facts, dict)
    if facts:
        assert facts["hostname"] == _device_r2()
        assert facts["vendor"] == "Arista"

def test_state_r2_loop0():
    output = connect.run_cmd(_device_r2(), "show ipv6 interface Loopback0 brief | include 2600:")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:bad:c0de::2/128" in output

def test_state_r2_ospf_neighbors():
    output = show.get_ospf_neighbors(_device_r2())
    assert output is not None and isinstance(output, str)
    assert "Neighbor 4.4.4.1 VRF default" in output

def test_state_r2_isis_neighbors():
    output = show.get_isis_neighbors(_device_r2())
    assert output is not None and isinstance(output, str)
    assert "CORE      default  s2               L2   Ethernet2" in output

def test_state_r2_config_drift():
    running = show.get_running(_device_r2())
    startup = show.get_startup(_device_r2())
    golden = show.get_golden(_device_r2())
    assert running is not None
    assert startup is not None
    assert golden is not None
    assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

####
# r3
####
def _device_r3():
    return _device("r3")

def test_state_r3_facts():
    facts = connect.get_facts(_device_r3())
    assert facts is not None and isinstance(facts, dict)
    if facts:
        assert facts["hostname"] == _device_r3()
        assert facts["vendor"] == "Cisco"

def test_state_r3_loop0():
    output = connect.run_cmd(_device_r3(), "show running-config interface loopback 0 | include ipv6 address")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:BAD:C0DE::3/128" in output

def test_state_r3_ospf_neighbors():
    output = show.get_ospf_neighbors(_device_r3())
    assert output is not None and isinstance(output, str)
    assert "3.3.3.1 " in output
    assert "4.4.4.0 " in output

def test_state_r3_bgp_neighbors():
    output = show.get_bgp_neighbors(_device_r3())
    assert output is not None and isinstance(output, str)
    assert r"BGP router identifier 3.3.3.0, local AS number 26" in output
    assert r"FE80::5%GigabitEthernet2" in output

def test_state_r3_config_drift():
    running = show.get_running(_device_r3())
    startup = show.get_startup(_device_r3())
    golden = show.get_golden(_device_r3())
    assert running is not None
    assert startup is not None
    assert golden is not None
    #assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

####
# r4
####
def _device_r4():
    return _device("r4")

def test_state_r4_facts():
    facts = connect.get_facts(_device_r4())
    assert facts is not None and isinstance(facts, dict)
    if facts:
        assert facts["hostname"] == _device_r4()
        assert facts["vendor"] == "Cisco"

def test_state_r4_loop0():
    output = connect.run_cmd(_device_r4(), "show running-config interface loopback 0 | include ipv6 address")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:BAD:C0DE::4/128" in output

def test_state_r4_ospf_neighbors():
    output = show.get_ospf_neighbors(_device_r4())
    assert output is not None and isinstance(output, str)
    assert "4.4.4.1 " in output
    assert "3.3.3.0 " in output

def test_state_r4_bgp_neighbors():
    output = show.get_bgp_neighbors(_device_r4())
    assert output is not None and isinstance(output, str)
    assert r"BGP router identifier 4.4.4.0, local AS number 26" in output
    assert r"FE80::5%GigabitEthernet2" in output

def test_state_r4_config_drift():
    running = show.get_running(_device_r4())
    startup = show.get_startup(_device_r4())
    golden = show.get_golden(_device_r4())
    assert running is not None
    assert startup is not None
    assert golden is not None
    #assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

####
# s1
####
def _device_s1():
    return _device("s1")

def test_state_s1_facts():
    facts = connect.get_facts(_device_s1())
    assert facts is not None and isinstance(facts, dict)
    if facts:
        assert facts["hostname"] == _device_s1()
        assert facts["vendor"] == "Arista"

def test_state_s1_loop0():
    output = connect.run_cmd(_device_s1(), "show ipv6 interface Loopback0 brief | include 2600:")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:bad:c0de::11/128" in output

def test_state_s1_isis_neighbors():
    output = show.get_isis_neighbors(_device_s1())
    assert output is not None and isinstance(output, str)
    assert "CORE      default  r1               L2   Ethernet1" in output
    assert "CORE      default  s2               L2   Ethernet2" in output

def test_state_s1_config_drift():
    running = show.get_running(_device_s1())
    startup = show.get_startup(_device_s1())
    golden = show.get_golden(_device_s1())
    assert running is not None
    assert startup is not None
    assert golden is not None
    assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

####
# s2
####
def _device_s2():
    return _device("s2")

def test_state_s2_facts():
    facts = connect.get_facts(_device_s2())
    assert facts is not None and isinstance(facts, dict)
    if facts:
        assert facts["hostname"] == _device_s2()
        assert facts["vendor"] == "Arista"

def test_state_s2_loop0():
    output = connect.run_cmd(_device_s2(), "show ipv6 interface Loopback0 brief | include 2600:")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:bad:c0de::12/128" in output

def test_state_s2_isis_neighbors():
    output = show.get_isis_neighbors(_device_s2())
    assert output is not None and isinstance(output, str)
    assert "CORE      default  r2               L2   Ethernet1" in output
    assert "CORE      default  s1               L2   Ethernet2" in output

def test_state_s2_config_drift():
    running = show.get_running(_device_s2())
    startup = show.get_startup(_device_s2())
    golden = show.get_golden(_device_s2())
    assert running is not None
    assert startup is not None
    assert golden is not None
    assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

####
# s3
####
def _device_s3():
    return _device("s3")

def test_state_s3_facts():
    facts = connect.get_facts(_device_s3())
    assert facts is not None and isinstance(facts, dict)
    if facts:
        assert facts["hostname"] == _device_s3()
        assert facts["vendor"] == "Arista"

def test_state_s3_loop0():
    output = connect.run_cmd(_device_s3(), "show ipv6 interface Loopback0 brief | include 2600:")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:bad:c0de::13/128" in output

def test_state_s3_ospf_neighbors():
    output = show.get_ospf_neighbors(_device_s3())
    assert output is not None and isinstance(output, str)
    assert "Neighbor 1.1.1.0 VRF default" in output
    assert "Neighbor 4.4.4.1 VRF default" in output
    assert "Neighbor 3.3.3.0 VRF default" in output

def test_state_s3_config_drift():
    running = show.get_running(_device_s3())
    startup = show.get_startup(_device_s3())
    golden = show.get_golden(_device_s3())
    assert running is not None
    assert startup is not None
    assert golden is not None
    assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

####
# s4
####
def _device_s4():
    return _device("s4")

def test_state_s4_facts():
    facts = connect.get_facts(_device_s4())
    assert facts is not None and isinstance(facts, dict)
    if facts:
        assert facts["hostname"] == _device_s4()
        assert facts["vendor"] == "Arista"

def test_state_s4_loop0():
    output = connect.run_cmd(_device_s4(), "show ipv6 interface Loopback0 brief | include 2600:")
    assert output is not None and isinstance(output, str)
    if output:
        assert "2600:bad:c0de::14/128" in output

def test_state_s4_ospf_neighbors():
    output = show.get_ospf_neighbors(_device_s4())
    assert output is not None and isinstance(output, str)
    assert "Neighbor 2.2.2.0 VRF default" in output
    assert "Neighbor 3.3.3.1 VRF default" in output
    assert "Neighbor 4.4.4.0 VRF default" in output

def test_state_s4_config_drift():
    running = show.get_startup(_device_s4())
    startup = show.get_running(_device_s4())
    golden = show.get_golden(_device_s4())
    assert running is not None
    assert startup is not None
    assert golden is not None
    assert show.build_side_by_side_diff(running, startup) == []
    assert show.build_side_by_side_diff(startup, golden) == []

def main():
    pass

if __name__ == "__main__":
    main()