import file_object
import pytest
from pathlib import Path

#######################
# Plain Text File Tests
#######################
def test_write_and_read_file_success(tmp_path: Path):
    target = tmp_path / "subdir" / "sample.txt"
    content = "Hello, network automation!"

    # write_file should create missing parent directories and write data
    assert file_object.write_file(target, content) is True
    assert target.is_file()

    # read_file should read the written string
    read_data = file_object.read_file(target)
    assert read_data == content
 
def test_read_file_nonexistent(tmp_path: Path):
    nonexistent = tmp_path / "does_not_exist.txt"
    assert file_object.read_file(nonexistent) is None

def test_read_file_directory_instead_of_file(tmp_path: Path):
    assert file_object.read_file(tmp_path) is None

#################
# JSON File Tests
#################
def test_write_and_read_json_success(tmp_path: Path):
    target = tmp_path / "data" / "payload.json"
    data = {"hostname": "rtr-core-01", "asn": 65001, "enabled": True}
    assert file_object.write_file_json(target, data) is True
    assert target.is_file()
    loaded = file_object.read_file_json(target)
    assert loaded == data

def test_read_json_missing_returns_default(tmp_path: Path):
    missing_file = tmp_path / "missing.json"
    assert file_object.read_file_json(missing_file, default={}) == {}
    assert file_object.read_file_json(missing_file) is None

def test_read_json_invalid_syntax_returns_default(tmp_path: Path):
    broken_file = tmp_path / "broken.json"
    broken_file.write_text("NOT_VALID_JSON: {")
    result = file_object.read_file_json(broken_file, default={"error": True})
    assert result == {"error": True}

def test_write_json_unserializable_object_returns_false(tmp_path: Path):
    target = tmp_path / "unserializable.json"
    # Sets cannot be directly serialized to JSON by default dump
    unserializable_data = {"key": {1, 2, 3}}
    assert file_object.write_file_json(target, unserializable_data) is False

#################
# YAML File Tests
#################
def test_write_and_read_yaml_success(tmp_path: Path):
    target = tmp_path / "configs" / "device.yaml"
    data = {
        "router1": {
            "vendor": "iosxr",
            "bgp": {"as": 65100, "neighbors": ["2001:db8::2"]}
        }
    }
    assert file_object.write_file_yaml(target, data) is True
    assert target.is_file()
    loaded = file_object.read_file_yaml(target)
    assert loaded == data

def test_read_yaml_missing_returns_default(tmp_path: Path):
    missing_file = tmp_path / "missing.yaml"
    assert file_object.read_file_yaml(missing_file, default=[]) == []

def test_read_yaml_empty_file_returns_default(tmp_path: Path):
    empty_file = tmp_path / "empty.yaml"
    empty_file.write_text("")

    # PyYAML safe_load on an empty file returns None; read_file_yaml falls back to default
    assert file_object.read_file_yaml(empty_file, default={"status": "empty"}) == {"status": "empty"}

def test_read_yaml_invalid_syntax_returns_default(tmp_path: Path):
    broken_file = tmp_path / "broken.yaml"
    broken_file.write_text("key: [unclosed list")
    assert file_object.read_file_yaml(broken_file, default=None) is None

def main():
    pass

if __name__ == "__main__":
    main()