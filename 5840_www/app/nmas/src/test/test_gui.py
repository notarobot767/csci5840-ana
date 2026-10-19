#!/usr/bin/env python3

from gui import add
import pytest

def test_get_vendors():
    vendors = add.get_vendors()
    assert vendors != None
    assert len(vendors) > 0
    assert isinstance(vendors, list)
    vendor_keys = [v[0] for v in vendors]
    assert "ios" in vendor_keys
    assert "iosxr" in vendor_keys
    assert "nxos" in vendor_keys
    assert "junos" in vendor_keys
    assert "eos" in vendor_keys

def test_templates():
    templates = add.get_templates()
    assert  templates is not None
    assert len(templates) > 0
    assert isinstance(templates, list)

def main():
    pass

if __name__ == "__main__":
    main()