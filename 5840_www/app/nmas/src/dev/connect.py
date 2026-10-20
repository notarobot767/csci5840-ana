#!/usr/bin/env python3

import copy
import signal
from contextlib import contextmanager
from napalm import get_network_driver
from napalm.base.exceptions import CommandErrorException, ConnectionException
import dev.creds
import subprocess
import ast

def ping6(target: str, count: int = 2, timeout: int = 2):
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
    conn.get_facts()
    return conn

@contextmanager
def time_limit(seconds: int):
    """Enforce a strict timeout using POSIX alarm signals."""
    def signal_handler(signum, frame):
        raise TimeoutError(f"Connection attempt timed out after {seconds} seconds.")

    # Register the signal handler and set the alarm
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        # Cancel the alarm once the block finishes
        signal.alarm(0)


def get_connection(device: str, max_retries: int = 3, timeout_sec: int = 3):
    cred = dev.creds.get_device_cred(device)
    if not cred:
        print(f"Device '{device}' not found in credentials.")
        return None

    hostname = cred.get("hostname")
    driver = cred.pop("driver")

    # Fast IPv6 ping check
    ping_res = subprocess.run(
        ["ping", "-6", "-c", "2", "-w", "2", hostname],
        capture_output=True,
        text=True
    )
    if ping_res.returncode != 0:
        print(f"Unable to ping: {hostname}")
        return None

    driver_cls = get_network_driver(driver)

    for attempt in range(1, max_retries + 1):
        try:
            # Enforce strict hard cutoff (kills SSL handshake stalls immediately)
            with time_limit(timeout_sec):
                conn = driver_cls(
                    hostname=hostname,
                    username=cred.get("username", "cisco"),
                    password=cred.get("password", "cisco"),
                    optional_args={"timeout": timeout_sec}
                )
                conn.open()
                return conn

        except TimeoutError:
            print(f"[Attempt {attempt}/{max_retries}] Device '{device}' stalled past {timeout_sec}s. Aborting and retrying...")
            continue
        except Exception as exc:
            print(f"[Attempt {attempt}/{max_retries}] Connection error on '{device}': {exc}")
            continue

    print(f"Failed to connect to '{device}' after {max_retries} attempts.")
    return None

def run_cmd(device: str, cmd: str) -> str | None:
    if device and cmd:
        try:
            conn = get_connection(device)
        except ConnectionException:
            return None

        if conn:
            try:
                result = conn.cli([cmd])
                return next(iter(result.values())).strip()
            except CommandErrorException as exc:
                err_payload = exc.args[0] if exc.args else str(exc)

                if isinstance(err_payload, dict):
                    return next(iter(err_payload.values())).strip()

                if isinstance(err_payload, str) and err_payload.strip().startswith("{"):
                    try:
                        parsed = ast.literal_eval(err_payload)
                        if isinstance(parsed, dict) and parsed:
                            return next(iter(parsed.values())).strip()
                    except (ValueError, SyntaxError):
                        pass

                return str(err_payload).strip()
            finally:
                conn.close()
    return None

def run_cmd_set(device: str, cmd_lst: list[str]) -> dict:
    pass

def get_facts(device: str) -> dict:
    conn = get_connection(device)
    if conn:
        return conn.get_facts()
    return None

def main():
    conn = get_connection("r3")
    print(conn.get_facts())
    conn.close()
    pass

if __name__ == "__main__":
    main()