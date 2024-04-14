# PAN-OS ZTP Patcher

The PAN-OS ZTP Patcher is a utility designed to streamline the process of updating the content version on PAN-OS firewalls during the Zero Touch Provisioning (ZTP) process. It leverages a Raspberry Pi Zero appliance to automate the content update procedure, eliminating the need for manual intervention.

## Use Case

When deploying PAN-OS firewalls in a network environment, it is often necessary to ensure that the firewalls have the latest content version installed. This content includes threat signatures, application definitions, and other critical updates that enhance the security posture of the firewalls.

The PAN-OS ZTP Patcher simplifies this process by automating the content update during the ZTP workflow. By connecting a Raspberry Pi Zero appliance to the management interface of the firewall and running this utility, the content version can be seamlessly updated without requiring manual steps.

Key benefits of using the PAN-OS ZTP Patcher:

- Automates the content update process during ZTP, saving time and effort.
- Ensures that PAN-OS firewalls have the latest content version installed from the start.
- Reduces the risk of human error associated with manual content updates.
- Enables faster and more efficient deployment of PAN-OS firewalls in network environments.

## Requirements

To use the PAN-OS ZTP Patcher, you need the following:

- Raspberry Pi Zero with Raspberry Pi OS and Python 3.7 or higher installed.
- USB to Ethernet adapter to connect the Raspberry Pi Zero to the management interface of the PAN-OS firewall.
- Ethernet interface on the Raspberry Pi Zero connected to the management interface of the PAN-OS firewall.
- Local IP address of 192.168.1.2/24 assigned to the Ethernet interface of the Raspberry Pi Zero.

## Installation

You can install the PAN-OS ZTP Patcher using pip:

```bash
pip install pan_ztp_patcher
```

## Usage

To use the PAN-OS ZTP Patcher, run the following command:

```bash
ztp_patcher --hostname <hostname> --username <username> --old-password <old_password> --new-password <new_password> [--pi-hostname <pi_hostname>] [--pi-content-path <pi_content_path>] [--content-file <content_file>]
```

- `<hostname>`: The hostname or IP address of the PAN-OS firewall.
- `<username>`: The username for accessing the PAN-OS firewall.
- `<old_password>`: The current password for the specified user on the PAN-OS firewall.
- `<new_password>`: The new password to be set for the specified user on the PAN-OS firewall.
- `<pi_hostname>` (optional): The hostname or IP address of the Raspberry Pi Zero appliance (default: 192.168.1.2).
- `<pi_content_path>` (optional): The path on the Raspberry Pi Zero where the content file is located (default: /var/tmp/).
- `<content_file>` (optional): The name of the content file to be installed on the PAN-OS firewall (default: panupv2-all-contents-8834-8684).

Example:

```bash
ztp_patcher --hostname 192.168.1.1 --username admin --old-password admin --new-password PaloAlto123!
```

The PAN-OS ZTP Patcher will perform the following steps:

1. Change the password of the specified user on the PAN-OS firewall.
2. Retrieve the API key from the PAN-OS firewall.
3. Import the content file from the Raspberry Pi Zero to the PAN-OS firewall using SCP.
4. Initiate the content update installation on the PAN-OS firewall using the API.
5. Monitor the content update job progress until completion.

Note: Ensure that the Raspberry Pi Zero is properly connected to the management interface of the PAN-OS firewall and has the necessary network connectivity before running the PAN-OS ZTP Patcher.

Please refer to the detailed documentation and examples provided with the PAN-OS ZTP Patcher for more information on its usage and advanced configuration options.

## License

The PAN-OS ZTP Patcher is released under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.
