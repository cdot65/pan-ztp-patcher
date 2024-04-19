# PAN-OS ZTP Patcher

The PAN-OS ZTP Patcher is a sophisticated Python utility designed to automate content version updates on PAN-OS firewalls during the Zero Touch Provisioning (ZTP) process. Utilizing a Raspberry Pi, this tool helps network administrators ensure their firewalls are always updated with the latest security features without manual intervention.

## Use Case

Deploying PAN-OS firewalls typically requires ensuring they are updated with the latest content versions, including threat signatures and application definitions. The PAN-OS ZTP Patcher automates these updates during the ZTP process, interfacing directly through a Raspberry Pi connected to the firewall's management interface.

### Key Benefits

- **Automated Content Updates**: Streamlines the ZTP process by automating updates, reducing time and effort.
- **Enhanced Security**: Ensures that firewalls receive the latest updates immediately upon deployment.
- **Reduced Human Error**: Minimizes the risks associated with manual updates.
- **Efficient Deployments**: Speeds up the setup process for PAN-OS firewalls with up-to-date configurations.

## Requirements

- Raspberry Pi with the latest OS and Python 3.7 or higher.
- USB to Ethernet adapter connecting the Raspberry Pi to the firewall's management interface.
- Configured network settings on the Raspberry Pi's Ethernet interface to 192.168.1.2/24.

## Installation

Install the PAN-OS ZTP Patcher via pip:

```bash
pip install pan-ztp-patcher
```

## Usage

Run the ZTP Patcher with the following command structure, providing the necessary parameters:

### Parameters

- `--env_file`: Path to the `.env` file containing environment variables (default: `.env`).
- `--pi_hostname`: Hostname or IP address of the Raspberry Pi.
- `--pi_username`: Username for the Raspberry Pi.
- `--pi_password`: Password for the Raspberry Pi.
- `--pan_hostname`: Hostname or IP address of the PAN-OS firewall.
- `--pan_username`: Username for the PAN-OS firewall.
- `--pan_password_new`: New password to be set for the firewall user.
- `--pan_password_old`: Current password for the firewall user.
- `--content_path`: Path on the Raspberry Pi where the content file is located.
- `--content_version`: Name of the content file to be installed.
- `--log_level`: Set the log level for the application; options are "DEBUG", "INFO", "WARNING", "ERROR" (default: "INFO").

### Example Commands

Execute with an .env file in the current working directory:

```bash
ztp_patcher --env_file .env
```

Execute by passing all values as arguments instead:

```bash
ztp_patcher \
--pi_hostname <pi_hostname> \
--pi_username <pi_username> \
--pi_password <pi_password> \
--pan_hostname <pan_hostname> \
--pan_username <pan_username> \
--pan_password_new <new_password> \
--pan_password_old <old_password> \
--content_path <content_path> \
--content_version <content_version> \
--log_level <log_level>
```

### Operational Steps

1. Changes the specified user's password on the PAN-OS firewall.
2. Retrieves the API key using the new credentials.
3. Imports and installs the content update from the Raspberry Pi using SCP.
4. Monitors the status of the content update job until completion.

Ensure proper connectivity and configurations are set before initiating the ZTP Patcher.

## Contributing

Contributions are welcome. Please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.
