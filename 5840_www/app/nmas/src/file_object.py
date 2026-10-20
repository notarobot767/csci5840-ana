#!/usr/bin/env python3

from json import load, dump
from pathlib import Path
from typing import Any
import yaml

def read_file(file: str | Path, encoding: str = "utf-8") -> str | None:
    """Read file and return contents as string, or None if reading fails."""
    try:
        path = Path(file)
        if not path.is_file():
            return None
        return path.read_text(encoding=encoding)
    except Exception:
        return None


def write_file(file: str | Path, data: str, encoding: str = "utf-8") -> bool:
    """Write string data to file. Returns True if successful, False otherwise."""
    try:
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding=encoding)
        return True
    except Exception:
        return False


def read_file_json(file: str | Path, default: Any = None) -> Any:
    """Read JSON file and return parsed content, or default if not found or invalid."""
    try:
        path = Path(file)
        if not path.is_file():
            return default
        with path.open("r", encoding="utf-8") as stream:
            return load(stream)
    except Exception:
        return default

def write_file_json(file: str | Path, data: Any, indent: int = 2) -> bool:
    """Write Python object to JSON file. Returns True if successful, False otherwise."""
    try:
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as stream:
            dump(data, stream, indent=indent)
        return True
    except Exception:
        return False


def read_file_yaml(file: str | Path, default: Any = None) -> Any:
    """Read YAML file and return parsed content, or default if not found or invalid."""
    try:
        path = Path(file)
        if not path.is_file():
            return default
        with path.open("r", encoding="utf-8") as stream:
            parsed = yaml.safe_load(stream)
            return default if parsed is None else parsed
    except Exception:
        return default


def write_file_yaml(file: str | Path, data: Any) -> bool:
    """Write Python object to YAML file. Returns True if successful, False otherwise."""
    try:
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as stream:
            yaml.safe_dump(data, stream, default_flow_style=False, sort_keys=False)
        return True
    except Exception:
        return False

def main():
    pass

if __name__ == "__main__":
    main()