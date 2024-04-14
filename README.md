# PAN-OS ZTP Patcher

This utility updates the content version on PAN-OS firewalls using a Raspberry Pi Zero appliance.

## Requirements

- Raspberry Pi Zero with Raspberry Pi OS and Python 3.7 or higher
- USB to Ethernet adapter
- Ethernet interface connected to the management interface of the PAN-OS firewall
- Local IP address of 192.168.1.2/24 assigned to the Ethernet interface

## Installation

```bash
pip install pan_ztp_patcher
```

## Usage

```bash
ztp_patcher <hostname> <username> <old_password> <new_password>
```
# pan-ztp-patcher
