#!/usr/bin/env python3

import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    hostname="2600:bad:c0de::1",  # r1 Loopback0 IPv6
    username="cisco",
    password="jm@O3s0411DQi@Qq",
    timeout=10,
)

channel = client.invoke_shell(term="vt100", width=512, height=1000)
time.sleep(2)
channel.send("terminal length 0\n")
time.sleep(1)
# Drain greeting/terminal length output
while channel.recv_ready():
    channel.recv(65535)

channel.send("show running-config\n")
time.sleep(3)

raw = b""
while channel.recv_ready():
    raw += channel.recv(65535)

print(f"BYTES RECEIVED: {len(raw)}")
print(repr(raw[:500]))  # First 500 bytes with escape codes visible
print(repr(raw[-500:]))  # Last 500 bytes where it stopped
client.close()