#!/usr/bin/env python3

import pytest
from dev import show, creds, connect


@pytest.fixture
def valid_device(request):
    """Ensure device is valid before executing test."""
    dev = request.param
    assert dev in creds.get_devices(), f"Device '{dev}' not found in credentials"
    return dev


# --- Facts Verification ---
@pytest.mark.parametrize(
    "valid_device,expected_vendor",
    [
        ("r1", "Arista"),
        ("r2", "Arista"),
        ("r3", "Cisco"),
        ("r4", "Cisco"),
        ("s1", "Arista"),
        ("s2", "Arista"),
        ("s3", "Arista"),
        ("s4", "Arista"),
    ],
    indirect=["valid_device"],
)
def test_device_facts(valid_device, expected_vendor):
    facts = connect.get_facts(valid_device)
    assert isinstance(facts, dict), f"Failed to retrieve facts for {valid_device}"
    assert facts.get("hostname") == valid_device
    assert facts.get("vendor") == expected_vendor


# --- Loopback IPv6 Verification ---
@pytest.mark.parametrize(
    "valid_device,cmd,expected_ip",
    [
        ("r1", "show ipv6 interface Loopback0 brief | include 2600:", "2600:bad:c0de::1/128"),
        ("r2", "show ipv6 interface Loopback0 brief | include 2600:", "2600:bad:c0de::2/128"),
        ("r3", "show running-config interface loopback 0 | include ipv6 address", "2600:BAD:C0DE::3/128"),
        ("r4", "show running-config interface loopback 0 | include ipv6 address", "2600:BAD:C0DE::4/128"),
        ("s1", "show ipv6 interface Loopback0 brief | include 2600:", "2600:bad:c0de::11/128"),
        ("s2", "show ipv6 interface Loopback0 brief | include 2600:", "2600:bad:c0de::12/128"),
        ("s3", "show ipv6 interface Loopback0 brief | include 2600:", "2600:bad:c0de::13/128"),
        ("s4", "show ipv6 interface Loopback0 brief | include 2600:", "2600:bad:c0de::14/128"),
    ],
    indirect=["valid_device"],
)
def test_loopback0_ipv6(valid_device, cmd, expected_ip):
    output = connect.run_cmd(valid_device, cmd)
    assert isinstance(output, str) and output.strip(), f"No output returned from {valid_device}"
    assert expected_ip in output


# --- Routing Adjacencies ---
@pytest.mark.parametrize(
    "valid_device,expected_neighbors",
    [
        ("r1", ["Neighbor 3.3.3.1 VRF default"]),
        ("r2", ["Neighbor 4.4.4.1 VRF default"]),
        ("r3", ["3.3.3.1 ", "4.4.4.0 "]),
        ("r4", ["4.4.4.1 ", "3.3.3.0 "]),
        ("s3", ["Neighbor 1.1.1.0 VRF default", "Neighbor 4.4.4.1 VRF default", "Neighbor 3.3.3.0 VRF default"]),
        ("s4", ["Neighbor 2.2.2.0 VRF default", "Neighbor 3.3.3.1 VRF default", "Neighbor 4.4.4.0 VRF default"]),
    ],
    indirect=["valid_device"],
)
def test_ospf_neighbors(valid_device, expected_neighbors):
    output = show.get_ospf_neighbors(valid_device)
    assert isinstance(output, str) and output.strip()
    for neighbor in expected_neighbors:
        assert neighbor in output


@pytest.mark.parametrize(
    "valid_device,expected_neighbors",
    [
        ("r1", ["CORE      default  s1               L2   Ethernet2"]),
        ("r2", ["CORE      default  s2               L2   Ethernet2"]),
        ("s1", ["CORE      default  r1               L2   Ethernet1", "CORE      default  s2               L2   Ethernet2"]),
        ("s2", ["CORE      default  r2               L2   Ethernet1", "CORE      default  s1               L2   Ethernet2"]),
    ],
    indirect=["valid_device"],
)
def test_isis_neighbors(valid_device, expected_neighbors):
    output = show.get_isis_neighbors(valid_device)
    assert isinstance(output, str) and output.strip()
    for neighbor in expected_neighbors:
        assert neighbor in output


# --- Configuration Drift ---
@pytest.mark.parametrize(
    "valid_device",
    ["r1", "r2", "r3", "r4", "s1", "s2", "s3", "s4"],
    indirect=["valid_device"],
)
def test_config_drift(valid_device):
    running = show.get_running(valid_device)
    startup = show.get_startup(valid_device)
    golden = show.get_golden(valid_device)

    assert running is not None, f"Could not retrieve running config for {valid_device}"
    assert startup is not None, f"Could not retrieve startup config for {valid_device}"
    assert golden is not None, f"Could not retrieve golden config for {valid_device}"

    assert show.build_side_by_side_diff(running, startup) == [], f"Running vs Startup drift on {valid_device}"
    assert show.build_side_by_side_diff(startup, golden) == [], f"Startup vs Golden drift on {valid_device}"