#!/usr/bin/env python3

from dev import show, creds
import pytest

def test_get_ospf_neighbors():
    """test if a random device can run this code"""
    device = creds.get_randon_device()
    output = show.get_ospf_neighbors(device)
    assert output is not None
    assert isinstance(output, str)

def test_get_ospf_neighbors_nonexistent():
    """test if a random device can run this code"""
    device = creds.get_nonexistent_device()
    output = show.get_ospf_neighbors(device)
    assert output is None

def test_get_bgp_neighbors():
    """test if a random device can run this code"""
    device = creds.get_randon_device()
    output = show.get_bgp_neighbors(device)
    assert output is not None
    assert isinstance(output, str)

def test_get_bgp_neighbors_nonexistent():
    """test if a random device can run this code"""
    device = creds.get_nonexistent_device()
    output = show.get_bgp_neighbors(device)
    assert output is None

def test_get_route_table():
    """test if a random device can run this code"""
    device = creds.get_randon_device()
    output = show.get_route_table(device)
    assert output is not None
    assert isinstance(output, str)
    driver = creds.get_driver(device)
    assert driver is not None and isinstance(driver, str)
    match driver:
        case "ios":
            assert "Codes: C - Connected, L - Local, S - Static, U - Per-user Static route" in output
        case "eos":
            assert "C - connected, S - static, K - kernel, O3 - OSPFv3," in output
        case _:
            assert False

def test_get_route_table_nonexistent():
    """test if a random device can run this code"""
    device = creds.get_nonexistent_device()
    output = show.get_route_table(device)
    assert output is None

def test_get_device_cpu():
    """test if a random device can run this code"""
    device = creds.get_randon_device()
    output = show.get_device_cpu(device)
    assert output is not None
    assert isinstance(output, str)
    driver = creds.get_driver(device)
    assert driver is not None and isinstance(driver, str)
    match driver:
            case "ios":
                assert "CPU utilization for" in output
            case "eos":
                assert "Tasks:" in output
            case _:
                assert False

def test_get_device_cpu_nonexistent():
    """test if a random device can run this code"""
    device = creds.get_nonexistent_device()
    output = show.get_device_cpu(device)
    assert output is None

def test_get_running():
    """test if a random device can run this code"""
    device = creds.get_randon_device()
    output = show.get_running(device)
    assert output is not None
    assert isinstance(output, str)
    assert "end" in output

def test_get_running_nonexistent():
    """test if a random device can run this code"""
    device = creds.get_nonexistent_device()
    output = show.get_running(device)
    assert output is None

def test_get_startup():
    """test if a random device can run this code"""
    device = creds.get_randon_device()
    output = show.get_startup(device)
    assert output is not None
    assert isinstance(output, str)
    assert "end" in output

def test_get_startup_nonexistent():
    """test if a random device can run this code"""
    device = creds.get_nonexistent_device()
    output = show.get_startup(device)
    assert output is None

def test_get_golden():
    """test if a random device can run this code"""
    device = creds.get_randon_device()
    output = show.get_golden(device)
    assert output is not None
    assert isinstance(output, str)
    assert "end" in output

def test_get_golden_nonexistent():
    """test if a random device can run this code"""
    device = creds.get_nonexistent_device()
    output = show.get_golden(device)
    assert output is None

def main():
    pass

if __name__ == "__main__":
    main()