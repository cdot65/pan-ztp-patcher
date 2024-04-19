# app.py

import argparse
import os
import sys

from dotenv import load_dotenv
from pan_ztp_patcher.utils import setup_logging
from pan_ztp_patcher.ztp_patcher import (
    change_firewall_password,
    check_content_version,
    download_software,
    copy_content_via_scp,
    install_latest_content_from_servers,
    install_specific_content_from_servers,
    install_content_via_usb,
    monitor_job_status,
    private_data_reset,
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

    Raises:
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
        "--pan_password_new",
        help="PAN-OS firewall password",
    )
    parser.add_argument(
        "--pan_password_old",
        help="Original default PAN-OS firewall password",
    )
    parser.add_argument(
        "--content_path",
        help="Content path on the Raspberry Pi",
    )
    parser.add_argument(
        "--content_version",
        help="Content version name",
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
    pan_password_new = args.pan_password_new or os.getenv("PAN_PASSWORD")
    pan_password_old = args.pan_password_old or os.getenv(
        "PAN_PASSWORD_DEFAULT"
    )

    # Raspberry Pi connection details
    pi_hostname = args.pi_hostname or os.getenv("PI_HOSTNAME")
    pi_username = args.pi_username or os.getenv("PI_USERNAME")
    pi_password = args.pi_password or os.getenv("PI_PASSWORD")
    content_path = args.content_path or os.getenv("CONTENT_PATH")
    content_version = args.content_version or os.getenv("CONTENT_FILE")

    # Validate the content_path argument
    if not os.path.isdir(content_path):
        parser.error(f"Invalid content path: {content_path}")

    # ------------------------------------------------------------------------
    # Set Up the PAN-OS Authentication Workflow
    # ------------------------------------------------------------------------
    changed_password = change_firewall_password(
        pan_hostname=pan_hostname,
        pan_password_new=pan_password_new,
        pan_password_old=pan_password_old,
        pan_username=pan_username,
    )

    if not changed_password:
        logger.error("Failed to change the firewall password.")
        # sys.exit(1)

    # Retrieve the API key
    api_key = retrieve_api_key(
        pan_hostname=pan_hostname,
        pan_password_new=pan_password_new,
        pan_username=pan_username,
    )

    if not api_key:
        logger.error("Failed to retrieve the API key.")
        sys.exit(1)

    logger.info("API key retrieved successfully.")

    # ------------------------------------------------------------------------
    # Retrieve License Workflow
    # ------------------------------------------------------------------------
    license_installed = retrieve_license(
        api_key=api_key,
        pan_hostname=pan_hostname,
    )

    # Check if the license was installed successfully
    if not license_installed:
        logger.error("Failed to retrieve the license.")
        sys.exit(1)

    logger.info("License retrieved successfully.")

    # ------------------------------------------------------------------------
    # Install Content Workflow
    # ------------------------------------------------------------------------
    max_attempts = 3
    attempt = 1

    while attempt <= max_attempts:
        jobs = {}
        jobs["id"] = {}
        jobs["result"] = {}

        logger.info(f"Attempt {attempt} of {max_attempts}")

        # --------------------------------------------------------------------
        # Check for the latest content version
        # --------------------------------------------------------------------
        jobs["id"]["check_content"] = check_content_version(
            api_key=api_key,
            content_version=content_version,
            pan_hostname=pan_hostname,
        )

        if jobs["id"]["check_content"]:
            logger.info(
                f"Monitoring download job status for job ID: {jobs['id']['check_content']}"
            )
            jobs["result"]["download_panw"] = monitor_job_status(
                api_key=api_key,
                job_id=jobs["id"]["check_content"],
                pan_hostname=pan_hostname,
            )

            if jobs["result"]["download_panw"]:
                logger.info(
                    "File downloaded successfully. Installing specific content from servers."
                )
                jobs["id"]["install_panw"] = (
                    install_specific_content_from_servers(
                        api_key=api_key,
                        content_version=content_version,
                        pan_hostname=pan_hostname,
                    )
                )

                if jobs["id"]["install_panw"]:
                    logger.info(
                        f"Monitoring install job status for job ID: {jobs['id']['install_panw']}"
                    )
                    jobs["result"]["install_panw"] = monitor_job_status(
                        api_key=api_key,
                        job_id=jobs["id"]["install_panw"],
                        pan_hostname=pan_hostname,
                    )

                    if jobs["result"]["install_panw"]:
                        logger.info(
                            "Specific content installed successfully from servers."
                        )
                    else:
                        logger.warning(
                            "Failed to install specific content from servers."
                        )
                else:
                    logger.error("Failed to retrieve the install job ID.")
            else:
                logger.warning("File download not completed successfully.")

        # --------------------------------------------------------------------
        # Download the software version from PANW servers
        # --------------------------------------------------------------------
        logger.info(
            f"Downloading software version {content_version} from PANW servers."
        )
        jobs["id"]["download_panw"] = download_software(
            api_key=api_key,
            content_version=content_version,
            pan_hostname=pan_hostname,
        )

        if jobs["id"]["download_panw"]:
            logger.info(
                f"Monitoring download job status for job ID: {jobs['id']['download_panw']}"
            )
            jobs["result"]["download_panw"] = monitor_job_status(
                api_key=api_key,
                job_id=jobs["id"]["download_panw"],
                pan_hostname=pan_hostname,
            )

            if jobs["result"]["download_panw"]:
                logger.info(
                    "File downloaded successfully. Installing specific content from servers."
                )
                jobs["id"]["install_panw"] = (
                    install_specific_content_from_servers(
                        api_key=api_key,
                        content_version=content_version,
                        pan_hostname=pan_hostname,
                    )
                )

                if jobs["id"]["install_panw"]:
                    logger.info(
                        f"Monitoring install job status for job ID: {jobs['id']['install_panw']}"
                    )
                    jobs["result"]["install_panw"] = monitor_job_status(
                        api_key=api_key,
                        job_id=jobs["id"]["install_panw"],
                        pan_hostname=pan_hostname,
                    )

                    if jobs["result"]["install_panw"]:
                        logger.info(
                            "Specific content installed successfully from servers."
                        )
                    else:
                        logger.warning(
                            "Failed to install specific content from servers."
                        )
                else:
                    logger.error("Failed to retrieve the install job ID.")
            else:
                logger.warning("File download not completed successfully.")

        # --------------------------------------------------------------------
        # Install Content From PANW Servers
        # --------------------------------------------------------------------
        jobs["id"]["panw_latest"] = install_latest_content_from_servers(
            api_key=api_key,
            pan_hostname=pan_hostname,
        )

        # if jobs["id"]["panw_latest"] is None, then log and increment attempt and continue
        if not jobs["id"]["panw_latest"]:
            logger.error("Failed to retrieve the job ID.")
            attempt += 1
            continue

        # Monitor the job status
        logger.info(
            f"Monitoring job status for job ID: {jobs['id']['panw_latest']}"
        )
        jobs["result"]["panw_latest"] = monitor_job_status(
            api_key=api_key,
            job_id=jobs["id"]["panw_latest"],
            pan_hostname=pan_hostname,
        )

        # If the job was successful, break out of the loop
        if jobs["result"]["panw_latest"]:
            logger.info("Content installed successfully from PANW servers.")
            break

        # If the job was not successful, attempt to download the software
        logger.warning(
            "Failed to install the content from servers, attempting to download software."
        )

        # --------------------------------------------------------------------
        # Import content using SCP
        # --------------------------------------------------------------------
        logger.info("Importing content via SCP from Raspberry Pi.")
        jobs["result"]["scp_copy"] = copy_content_via_scp(
            content_path=content_path,
            content_version=content_version,
            pan_hostname=pan_hostname,
            pan_password_new=pan_password_new,
            pan_username=pan_username,
            pi_hostname=pi_hostname,
            pi_password=pi_password,
            pi_username=pi_username,
        )

        # Exit the execution if jobs["result"]["scp_install"] is False
        if not jobs["result"]["scp_copy"]:
            logger.error("Failed to import the content via SCP.")
            attempt += 1
            continue

        # Install content using the API
        logger.info("Installing content via USB.")
        jobs["id"]["install_usb"] = install_content_via_usb(
            api_key=api_key,
            content_version=content_version,
            pan_hostname=pan_hostname,
        )

        # Monitor the job status
        if jobs["result"]["install_usb"]:
            logger.info(
                f"Monitoring job status for job ID: {jobs['result']['install_usb']}"
            )
            jobs["result"]["install_usb"] = monitor_job_status(
                api_key=api_key,
                job_id=jobs["id"]["install_usb"],
                pan_hostname=pan_hostname,
            )
        else:
            logger.error("Failed to retrieve the job ID.")
            attempt += 1
            continue

        if jobs["result"]["install_usb"]:
            logger.info("Content installed successfully via USB.")
            break
        else:
            logger.warning("Failed to install the content via USB.")
            logger.debug(jobs)
            attempt += 1

    if attempt > max_attempts:
        logger.error("Failed to install the content after multiple attempts.")
        sys.exit(1)

    # ------------------------------------------------------------------------
    # Private Data Reset Workflow
    # ------------------------------------------------------------------------
    max_attempts = 3
    attempt = 1

    while attempt <= max_attempts:
        reset = private_data_reset(
            api_key=api_key,
            pan_hostname=pan_hostname,
        )

        if reset:
            logger.info("Firewall data successfully reset.")
            break
        else:
            logger.warning("Failed to reset the firewall data.")
            attempt += 1


if __name__ == "__main__":
    main()
