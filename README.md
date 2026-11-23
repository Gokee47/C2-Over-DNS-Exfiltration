# The Autonomous C2-Over-DNS Exfiltration Pipeline

## Overview
This project demonstrates a stealthy Command & Control (C2) channel and data exfiltration technique using DNS Tunneling. By exploiting the fact that perimeter firewalls must allow DNS (UDP Port 53) for basic connectivity, this lab bypasses strict egress filtering to steal sensitive files and remotely control a victim machine.

## Lab Architecture
- **Victim (VM1):** Ubuntu 22.04 (IP: 192.168.10.10) + Zeek Sensor
- **Firewall (VM2):** pfSense (Blocks HTTP/HTTPS/ICMP; Allows only UDP 53)
- **Resolver (VM3):** Ubuntu 22.04 with BIND9 (Forwards *.evil.com to Attacker)
- **Attacker (VM4):** Kali Linux (IP: 192.168.20.100)

## How It Works
1. **Exfiltration:** The implant reads `/etc/passwd`, compresses it (Gzip), Base32-encodes it, and sends it in 60-character chunks via DNS A-record queries (`chunk.seq.data.evil.com`).
2. **C2 Channel:** The attacker's server sends commands (`whoami`, `id`) via DNS TXT records. The victim executes them and sends the output back via DNS A-records.
3. **Blue Team:** Zeek is used on the victim to monitor DNS traffic. A Python script parses the `dns.log` to detect suspicious queries.

## Repository Structure
- `attacker/c2_server.py` - Custom Python DNS C2 Server.
- `victim/implant.py` - Python implant for exfiltration and C2.
- `blue_team/detect_dns.py` - Python script for Zeek log analysis.
- `REPORT.pdf` - Full project documentation.
