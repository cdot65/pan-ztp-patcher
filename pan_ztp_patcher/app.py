import argparse
import logging
from logging.handlers import RotatingFileHandler
from pan_ztp_patcher.ztp_patcher import (
    change_password,
    get_api_key,
    scp_import_content,
    send_api_request,
    job_monitor,
)


def main():
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Configure file handler for debug level
    file_handler = RotatingFileHandler(
        "debug.log", maxBytes=5 * 1024 * 1024, backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )  # noqa E501
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Configure console handler for info level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Update content version on PAN-OS firewalls",
    )
    parser.add_argument(
        "-H",
        "--hostname",
        required=True,
        help="Firewall hostname or IP address",
    )
    parser.add_argument(
        "-u",
        "--username",
        required=True,
        help="Firewall username",
    )
    parser.add_argument(
        "-o",
        "--old-password",
        required=True,
        help="Firewall old password",
    )
    parser.add_argument(
        "-n",
        "--new-password",
        required=True,
        help="Firewall new password",
    )
    parser.add_argument(
        "-p",
        "--pi-hostname",
        default="192.168.1.2",
        help="Raspberry Pi hostname or IP address (default: 192.168.1.2)",
    )
    parser.add_argument(
        "-d",
        "--pi-content-path",
        default="/var/tmp/",
        help="Raspberry Pi content path (default: /var/tmp/)",
    )
    parser.add_argument(
        "-f",
        "--content-file",
        default="panupv2-all-contents-8834-8684",
        help="Content file name (default: panupv2-all-contents-8834-8684)",
    )
    args = parser.parse_args()

    # Firewall connection details
    hostname = args.hostname
    username = args.username
    old_password = args.old_password
    new_password = args.new_password

    # Raspberry Pi connection details
    pi_hostname = args.pi_hostname
    pi_content_path = args.pi_content_path
    content_file = args.content_file

    # Call the functions
    change_password(
        hostname,
        username,
        old_password,
        new_password,
    )
    api_key = get_api_key(
        hostname,
        username,
        new_password,
    )
    if api_key:
        logger.info("API Key: {}".format(api_key))
    else:
        logger.error("Failed to retrieve the API key.")
        return

    scp_import_content(
        hostname,
        username,
        new_password,
        pi_hostname,
        pi_content_path,
        content_file,
    )
    job_id = send_api_request(
        hostname,
        api_key,
        content_file,
    )
    if job_id:
        job_monitor(
            hostname,
            api_key,
            job_id,
        )
    else:
        logger.error("Failed to retrieve the job ID.")


if __name__ == "__main__":
    main()
