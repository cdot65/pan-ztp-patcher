import argparse
import os

from dotenv import load_dotenv
from pan_ztp_patcher.constants import (
    DEFAULT_CONTENT_FILE,
    DEFAULT_CONTENT_PATH,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PAN_HOSTNAME,
    DEFAULT_PAN_PASSWORD,
    DEFAULT_PAN_PASSWORD_DEFAULT,
    DEFAULT_PAN_USERNAME,
)
from pan_ztp_patcher.utils import setup_logging
from pan_ztp_patcher.ztp_patcher import (
    change_firewall_password,
    import_content_via_scp,
    install_content_via_api,
    monitor_job_status,
    retrieve_api_key,
)


def main():
    """
    Main function that orchestrates the PAN-OS firewall content update process.

    This function performs the following steps:
    1. Loads environment variables from the .env file.
    2. Configures logging.
    3. Parses command-line arguments.
    4. Validates the content_path argument.
    5. Retrieves the API key from the PAN-OS firewall.
    6. Imports content using SCP.
    7. Sends an API request to install the content.
    8. Monitors the job status.

    Returns:
        None
    """

    # Load environment variables from .env file
    load_dotenv()

    # Configure logging
    logger = setup_logging()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Update content version on PAN-OS firewalls",
    )
    parser.add_argument(
        "--pi_hostname",
        default=os.environ.get("PI_HOSTNAME"),
        required=True,
        help="Raspberry Pi hostname or IP address",
    )
    parser.add_argument(
        "--pi_username",
        default=os.environ.get("PI_USERNAME"),
        required=True,
        help="Raspberry Pi username",
    )
    parser.add_argument(
        "--pi_password",
        default=os.environ.get("PI_PASSWORD"),
        required=True,
        help="Raspberry Pi password",
    )
    # Parse command-line arguments
    parser.add_argument(
        "--pan_hostname",
        default=os.environ.get("PAN_HOSTNAME", DEFAULT_PAN_HOSTNAME),
        help=f"PAN-OS firewall hostname or IP address (default: {DEFAULT_PAN_HOSTNAME})",  # noqa E501
    )
    parser.add_argument(
        "--pan_username",
        default=os.environ.get("PAN_USERNAME", DEFAULT_PAN_USERNAME),
        help=f"PAN-OS firewall username (default: {DEFAULT_PAN_USERNAME})",
    )
    parser.add_argument(
        "--pan_password",
        default=os.environ.get("PAN_PASSWORD", DEFAULT_PAN_PASSWORD),
        help=f"PAN-OS firewall password (default: {DEFAULT_PAN_PASSWORD})",
    )
    parser.add_argument(
        "--pan_password_default",
        default=os.environ.get(
            "PAN_PASSWORD_DEFAULT", DEFAULT_PAN_PASSWORD_DEFAULT
        ),  # noqa E501
        help=f"Original default PAN-OS firewall password (default: {DEFAULT_PAN_PASSWORD_DEFAULT})",  # noqa E501
    )
    parser.add_argument(
        "--content_path",
        default=os.environ.get("CONTENT_PATH", DEFAULT_CONTENT_PATH),
        help=f"Content path on the Raspberry Pi (default: {DEFAULT_CONTENT_PATH})",  # noqa E501
    )
    parser.add_argument(
        "--content_file",
        default=os.environ.get("CONTENT_FILE", DEFAULT_CONTENT_FILE),
        help=f"Content file name (default: {DEFAULT_CONTENT_FILE})",
    )
    parser.add_argument(
        "--log_level",
        default=os.environ.get("LOG_LEVEL", DEFAULT_LOG_LEVEL),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help=f"Set the log level (default: {DEFAULT_LOG_LEVEL})",
    )

    args = parser.parse_args()

    # Validate the content_path argument
    content_path = args.content_path
    if not os.path.isdir(content_path):
        parser.error(f"Invalid content path: {content_path}")

    # Firewall connection details
    pan_hostname = args.pan_hostname
    pan_username = args.pan_username
    pan_password = args.pan_password
    pan_password_default = args.pan_password_default

    # Raspberry Pi connection details
    pi_hostname = args.pi_hostname
    pi_username = args.pi_username
    pi_password = args.pi_password
    content_path = args.content_path
    content_file = args.content_file

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
        logger.info("API Key: {}".format(api_key))
    else:
        logger.error("Failed to retrieve the API key.")
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
