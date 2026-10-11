#!/usr/bin/env python3

import dev.creds, file_object

from napalm import get_network_driver
import concurrent.futures
import copy
import subprocess

def ping6(target: str, count: int = 2, timeout: int = 2) -> bool:
    cmd = ["ping", "-6", "-c", str(count), "-w", str(timeout), target]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return result

def _open_and_test(driver_cls, cred):
    conn = driver_cls(**cred)
    conn.open()
    conn.cli(["show clock"])
    return conn

def get_connection(device: str):
    cred = dev.creds.get_device_cred(device)
    hostname = cred.get("hostname", None)
    driver = cred.pop("driver")

    if not ping6(hostname).returncode == 0:
        print(f"unable to ping: {hostname}")
        return None

    driver_cls = get_network_driver(driver)

  # For Arista EOS, attempt fast probe using threadpool timeout
    if driver == "eos":
        for attempt in range(1, 4):
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = executor.submit(
                _open_and_test, driver_cls, copy.deepcopy(cred)
            )
            try:
                # Enforce 2.0 second hard cutoff per attempt
                conn = future.result(timeout=2.0)
                executor.shutdown(wait=False)
                return conn
            except (concurrent.futures.TimeoutError, Exception):
                executor.shutdown(wait=False)
                continue

  # Standard connection for Cisco IOS (or EOS fallback)
    try:
        conn = driver_cls(**cred)
        conn.open()
        return conn
    except Exception as exc:
        print(f"Error connecting to {device}[{hostname}]: {exc}")
        return None

def run_cmd(device: str, cmd: str) -> str:
    if dev and cmd:
        conn = get_connection(device)
        if conn:
            try:
                result = conn.cli([cmd])
                return next(iter(result.values())).strip()
            finally:
                conn.close()
    return None

def run_cmd_set(device: str, cmd_lst: list[str]) -> dict:
    pass

def main():
    print(ping6(dev.creds.get_hostname("r1")).stdout)

if __name__ == "__main__":
    main()