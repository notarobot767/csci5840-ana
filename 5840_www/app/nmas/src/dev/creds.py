#!/usr/bin/env python3

import file_object

def get_creds():
  cred_file = "../device_creds.yaml"
  return file_object.read_file_yaml(cred_file)

def get_device_cred(device):
  return get_creds()[device]

def main():
  pass

if __name__ == "__main__":
  main()