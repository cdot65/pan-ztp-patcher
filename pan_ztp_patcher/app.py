# app.py

import argparse
import os
from dotenv import load_dotenv
from pan_ztp_patcher.utils import setup_logging
from pan_ztp_patcher.ztp_patcher import (
    change_firewall_password,
    import_content_via_scp,
    install_content_via_api,
    monitor_job_status,
    retrieve_api_key,
    retrieve_license,
)


def main():
    """
    Main function that orchestrates the PAN-OS firewall content update process.

    This function performs the following steps:
    1. Configures logging.
    2. Parses command-line arguments.
    3. Loads any .env file
    4. Validates the content_path argument.
    5. Retrieves the API key from the PAN-OS firewall.
    6. Imports content using SCP.
    7. Sends an API request to install the content.
    8. Monitors the job status.

    Returns:
        None
    """

    # Configure logging
    logger = setup_logging()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Update content version on PAN-OS firewalls",
    )
    parser.add_argument(
        "--env_file",
        default=".env",
        help="Path to the .env file (default: .env)",
    )
    parser.add_argument(
        "--pi_hostname",
        help="Raspberry Pi hostname or IP address",
    )
    parser.add_argument(
        "--pi_username",
        help="Raspberry Pi username",
    )
    parser.add_argument(
        "--pi_password",
        help="Raspberry Pi password",
    )
    parser.add_argument(
        "--pan_hostname",
        help="PAN-OS firewall hostname or IP address",
    )
    parser.add_argument(
        "--pan_username",
        help="PAN-OS firewall username",
    )
    parser.add_argument(
        "--pan_password",
        help="PAN-OS firewall password",
    )
    parser.add_argument(
        "--pan_password_default",
        help="Original default PAN-OS firewall password",
    )
    parser.add_argument(
        "--content_path",
        help="Content path on the Raspberry Pi",
    )
    parser.add_argument(
        "--content_file",
        help="Content file name",
    )
    parser.add_argument(
        "--log_level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the log level (default: INFO)",
    )

    args = parser.parse_args()

    # Load environment variables from the specified .env file
    load_dotenv(args.env_file)

    # Firewall connection details
    pan_hostname = args.pan_hostname or os.getenv("PAN_HOSTNAME")
    pan_username = args.pan_username or os.getenv("PAN_USERNAME")
    pan_password = args.pan_password or os.getenv("PAN_PASSWORD")
    pan_password_default = args.pan_password_default or os.getenv(
        "PAN_PASSWORD_DEFAULT"
    )

    # Raspberry Pi connection details
    pi_hostname = args.pi_hostname or os.getenv("PI_HOSTNAME")
    pi_username = args.pi_username or os.getenv("PI_USERNAME")
    pi_password = args.pi_password or os.getenv("PI_PASSWORD")
    content_path = args.content_path or os.getenv("CONTENT_PATH")
    content_file = args.content_file or os.getenv("CONTENT_FILE")

    # Validate the content_path argument
    if not os.path.isdir(content_path):
        parser.error(f"Invalid content path: {content_path}")

    # Change the default firewall password
    change_firewall_password(
        pan_hostname,
        pan_username,
        pan_password,
        pan_password_default,
    )

    # Retrieve the API key
    api_key = retrieve_api_key(
        pan_hostname,
        pan_username,
        pan_password,
    )
    if api_key:
        logger.info("API Key retrieved successfully.")
    else:
        logger.error("Failed to retrieve the API key.")
        return

    license_job = retrieve_license(
        pan_hostname,
        api_key,
    )
    if license_job:
        logger.info("License retrieved successfully.")
    else:
        logger.error("Failed to retrieve the license.")
        return

    # Import content using SCP
    import_content_via_scp(
        pan_hostname,
        pan_username,
        pan_password,
        pi_hostname,
        pi_username,
        pi_password,
        content_path,
        content_file,
    )

    # Install content using the API
    job_id = install_content_via_api(
        pan_hostname,
        api_key,
        content_file,
    )
    if job_id:
        monitor_job_status(
            pan_hostname,
            api_key,
            job_id,
        )
    else:
        logger.error("Failed to retrieve the job ID.")


if __name__ == "__main__":
    main()
