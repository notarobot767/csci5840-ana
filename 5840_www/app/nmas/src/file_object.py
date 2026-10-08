#!/usr/bin/env python3

from json import load
from pathlib import Path
from typing import Any
import yaml

def read_file(file):
    """read file and return contents"""
    with open(file) as file_reader:
        return file_reader.read()
    
def write_file(file, data):
    """write contents of data to file"""
    with open(file, "w") as file_writer:
        file_writer.write(data)

def read_file_json(file):
    """read file as return contents as json object"""
    with open(file) as file_reader:
        return load(file_reader)

def read_file_yaml(file: str | Path) -> Any:
    """Safely read and parse a YAML file into Python objects."""
    path = Path(file)
    if not path.is_file():
        raise FileNotFoundError(f"YAML file not found at: {path}")

    with path.open("r", encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise ValueError(f"Error parsing YAML file: {exc}") from exc

def main():
    pass

if __name__ == "__main__":
    main()