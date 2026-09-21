#!/usr/bin/env python3

from json import load
import yaml

def read_file(file):
    """read file and return contents"""
    with open(file) as file_reader:
        return file_reader.read()
    
def write_file(file, data, mode="w"):
    """write contents of data to file"""
    with open(file, mode) as file_writer:
        file_writer.write(data)

def read_file_json(file):
    """read file as return contents as json object"""
    with open(file) as file_reader:
        return load(file_reader)
    
def read_file_yaml(file):
    """read file as return contents as yaml object"""
    with open(file) as file_reader:
        return yaml.safe_load(file_reader)