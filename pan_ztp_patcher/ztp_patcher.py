import logging
import paramiko
import time
import urllib.request
import xml.etree.ElementTree as ET

from typing import Optional

logger = logging.getLogger(__name__)


def change_firewall_password(
    pan_hostname: str,
    pan_password_new: str,
    pan_password_old: str,
    pan_username: str,
) -> bool:
    """
    Changes the password of a user on the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        pan_username (str): The username for authentication.
        pan_password_new (str): The new password to set for the user.
        pan_password_old (str): The current password of the user.

    Returns:
        bool: True if the password change is successful, False otherwise.

    Raises:
        paramiko.AuthenticationException: If authentication fails.
        paramiko.SSHException: If an SSH exception occurs.
        Exception: If any other error occurs during the password change process.
    """

    logger.info("=" * 79)
    logger.info("Changing firewall password...")
    logger.info("=" * 79)

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the firewall
        logger.debug("Connecting to {}...".format(pan_hostname))
        client.connect(
            hostname=pan_hostname,
            username=pan_username,
            password=pan_password_old,
        )
        logger.info("Connected to {} successfully.".format(pan_hostname))

        # Create an interactive shell
        shell = client.invoke_shell()

        # Wait for the prompt
        logger.debug("Waiting for the prompt...")
        time.sleep(3)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the old password
        logger.debug("Sending pan_password_old: {}".format(pan_password_old))
        shell.send(pan_password_old + "\n")
        time.sleep(3)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the new password
        logger.debug("Sending pan_password_new: {}".format(pan_password_new))
        shell.send(pan_password_new + "\n")
        time.sleep(3)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Confirm the new password
        logger.debug("Confirming pan_password_new: {}".format(pan_password_new))
        shell.send(pan_password_new + "\n")
        time.sleep(3)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Close the SSH connection
        logger.debug("Closing the SSH connection...")
        client.close()
        logger.info("Password changed successfully.")
        return True

    except paramiko.AuthenticationException:
        logger.error("Authentication failed. Please check your credentials.")
        return False

    except paramiko.SSHException as ssh_exception:
        logger.error("SSH exception occurred: {}".format(str(ssh_exception)))
        return False

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return False


def check_content_version(
    api_key: str,
    content_version: str,
    pan_hostname: str,
) -> bool:
    """
    Checks if the specified content version (filename) is available from the PANW servers.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.
        content_version (str): The content version (filename) to check for.

    Returns:
        bool: True if the content version (filename) is found, False otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the API request.
    """

    logger.info("=" * 79)
    logger.info(
        f"Attempting to check if content version (filename) {content_version} is available"
    )
    logger.info("=" * 79)

    try:
        # Construct the API URL
        url = "https://{}/api/?type=op&cmd={}".format(
            pan_hostname,
            urllib.parse.quote_plus(
                "<request><content><upgrade><check/></upgrade></content></request>"
            ),
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        request = urllib.request.Request(url)
        request.add_header("X-PAN-KEY", api_key)

        # Send the API request
        logger.debug("Sending API request...")
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )

        # Read the response content
        logger.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logger.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Check the response status
        if root.attrib.get("status") == "success":
            # Find all 'entry' elements in the XML response
            entries = root.findall(".//entry")

            # Iterate over each 'entry' element
            for entry in entries:
                # Find the 'filename' element within the 'entry'
                filename_element = entry.find("filename")

                # Check if the 'filename' element exists and matches the specified content version
                if (
                    filename_element is not None
                    and filename_element.text == content_version
                ):
                    logger.info(
                        f"Content version (filename) {content_version} found."
                    )
                    return True

            # If the content version is not found in any entry
            logger.info(
                f"Content version (filename) {content_version} not found."
            )
            return False

        else:
            error_message = root.find("./msg/line")
            if error_message is not None:
                logger.error(
                    "API request failed: {}".format(error_message.text)
                )
            else:
                logger.error("API request failed.")
            return False

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
        return False

    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
        return False

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return False


def copy_content_via_scp(
    content_path: str,
    content_version: str,
    pan_hostname: str,
    pan_password_new: str,
    pan_username: str,
    pi_hostname: str,
    pi_password: str,
    pi_username: str,
) -> Optional[bool]:
    """
    Imports content to the PAN-OS firewall using SCP.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        pan_username (str): The username for authentication.
        pan_password_new (str): The password for authentication.
        pi_hostname (str): The hostname or IP address of the Raspberry Pi.
        content_path (str): The path to the content file on the Raspberry Pi.
        content_version (str): The name of the content file.
        pi_username (str): The username for authentication on the Raspberry Pi.
        pi_password (str): The password for authentication on the Raspberry Pi.

    Returns:
        Optional[bool]: True if the SCP import is successful, False otherwise.

    Raises:
        paramiko.AuthenticationException: If authentication fails.
        paramiko.SSHException: If an SSH exception occurs.
        Exception: If any other error occurs during the SCP import process.
    """

    logger.info("=" * 79)
    logger.info("Importing content via SCP...")
    logger.info("=" * 79)

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the firewall
        logger.debug("Connecting to {}...".format(pan_hostname))
        client.connect(
            hostname=pan_hostname,
            username=pan_username,
            password=pan_password_new,
        )
        logger.info("Connected to {} successfully.".format(pan_hostname))

        # Create an interactive shell
        shell = client.invoke_shell()

        # Wait for the prompt
        logger.debug("Waiting for the prompt...")
        time.sleep(3)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the scp import command
        scp_command = "scp import content from {}@{}:{}/{}".format(
            pi_username,
            pi_hostname,
            content_path,
            content_version,
        )
        logger.debug("Sending SCP command: {}".format(scp_command))
        shell.send(scp_command + "\n")
        time.sleep(5)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Check if the host authenticity prompt appears
        logger.debug("Checking for host authenticity prompt...")
        if (
            "Please type 'yes', 'no' or the fingerprint" in output
            or "Are you sure you want to continue connecting" in output
        ):
            logger.debug("Sending 'yes' to the prompt...")
            shell.send("yes\n")
            time.sleep(3)
            output = shell.recv(1024).decode("utf-8")
            logger.debug("Received output: {}".format(output))

        # Send the password for the Raspberry Pi
        logger.debug(
            "Sending password for {}@{}...".format(pi_username, pi_hostname)
        )
        time.sleep(3)
        shell.send(pi_password + "\n")
        time.sleep(3)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Wait for the completion prompt
        logger.debug("Waiting for the completion prompt...")
        start_time = time.time()
        while True:
            if time.time() - start_time > 120:
                logger.error(
                    "Timeout occurred while waiting for the completion prompt."
                )

                # Close the SSH connection
                client.close()
                return False

            output += shell.recv(1024).decode("utf-8")
            logger.debug("Received output: {}".format(output))

            # Check if the content file already exists
            if "already exists" in output:
                logger.info("Content file already exists on the firewall.")

                # Close the SSH connection
                client.close()
                return True

            # Check if the import is completed
            elif "saved" in output and "ETA" not in output:
                logger.debug("SCP import content completed successfully.")
                logger.info("SCP import content completed successfully.")

                # Close the SSH connection
                client.close()
                return True

            # Wait for 3 seconds before the next iteration
            time.sleep(3)

    except paramiko.AuthenticationException:
        logger.error("Authentication failed. Please check your credentials.")
        return False

    except paramiko.SSHException as ssh_exception:
        logger.error("SSH exception occurred: {}".format(str(ssh_exception)))
        return False

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return False


def download_software(
    api_key: str,
    content_version: str,
    pan_hostname: str,
) -> Optional[str]:
    """
    Downloads the specified software version from the PANW servers.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.
        content_version (str): The version of the software to download.

    Returns:
        Optional[str]: The job ID if the API request is successful, None otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the API request.
    """

    logger.info("=" * 79)
    logger.info(
        "Attempting to download software version: {}".format(content_version)
    )
    logger.info("=" * 79)

    try:
        # Construct the API URL
        url = "https://{}/api/?type=op&cmd={}".format(
            pan_hostname,
            urllib.parse.quote_plus(
                "<request><content><upgrade><download><file>{}</file></download></upgrade></content></request>".format(
                    content_version
                )
            ),
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        request = urllib.request.Request(url)
        request.add_header("X-PAN-KEY", api_key)

        # Send the API request
        logger.debug("Sending API request...")
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )

        # Read the response content
        logger.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logger.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Check the response status
        if root.attrib.get("status") == "success":
            job_element = root.find("./result/job")

            # Extract the job ID from the response
            if job_element is not None:
                job_id = job_element.text
                logger.info(
                    "API request successful. Job ID: {}".format(job_id),
                )
                return job_id

            # Log an error if the job ID is not found
            else:
                logger.error("Job ID not found in the response.")
                return None

        else:
            error_message = root.find("./msg/line")
            if error_message is not None:
                logger.error(
                    "API request failed: {}".format(error_message.text)
                )
            else:
                logger.error("API request failed.")
            return None

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
        return None

    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
        return None

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return None


def install_content_via_usb(
    api_key: str,
    content_version: str,
    pan_hostname: str,
) -> Optional[str]:
    """
    Sends an API request to install the content on the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.
        content_version (str): The name of the content file to install.

    Returns:
        Optional[str]: The job ID if the API request is successful, None otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the API request.
    """

    logger.info("=" * 79)
    logger.info("Attempting to update content from USB...")
    logger.info("=" * 79)

    try:
        # Construct the API URL
        url = "https://{}/api/?type=op&cmd={}".format(
            pan_hostname,
            urllib.parse.quote_plus(
                "<request><content><upgrade><install><file>{}</file></install></upgrade></content></request>".format(
                    content_version
                )
            ),
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        request = urllib.request.Request(url)
        request.add_header("X-PAN-KEY", api_key)

        # Send the API request
        logger.debug("Sending API request...")
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )

        # Read the response content
        logger.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logger.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Check the response status
        if root.attrib.get("status") == "success":
            job_element = root.find("./result/job")

            # Extract the job ID from the response
            if job_element is not None:
                job_id = job_element.text
                logger.info("API request successful. Job ID: {}".format(job_id))
                return job_id

            # Log an error if the job ID is not found
            else:
                logger.error("Job ID not found in the response.")
                return None

        else:
            error_message = root.find("./msg/line")
            if error_message is not None:
                logger.error(
                    "API request failed: {}".format(error_message.text)
                )
            else:
                logger.error("API request failed.")
            return None

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
        return None

    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))

        return None
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return None


def install_latest_content_from_servers(
    pan_hostname: str,
    api_key: str,
) -> Optional[str]:
    """
    Sends an API request to install the latest content from the PANW servers.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.

    Returns:
        Optional[str]: The job ID if the API request is successful, None otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the API request.
    """

    logger.info("=" * 79)
    logger.info("Attempting to update content from public PANW servers...")
    logger.info("=" * 79)

    try:
        # Construct the API URL
        url = "https://{}/api/?type=op&cmd={}".format(
            pan_hostname,
            urllib.parse.quote_plus(
                "<request><content><upgrade><install><version>latest</version></install></upgrade></content></request>"
            ),
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        request = urllib.request.Request(url)
        request.add_header("X-PAN-KEY", api_key)

        # Send the API request
        logger.debug("Sending API request...")
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )

        # Read the response content
        logger.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logger.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Check the response status
        if root.attrib.get("status") == "success":
            job_element = root.find("./result/job")

            # Extract the job ID from the response
            if job_element is not None:
                job_id = job_element.text
                logger.info("API request successful. Job ID: {}".format(job_id))
                return job_id

            # Log an error if the job ID is not found
            else:
                logger.error("Job ID not found in the response.")
                return None

        elif root.attrib.get("line") > 0:
            logger.error(
                "API request failed: {}".format(root.attrib.get("line"))
            )
            return None

        else:
            logger.error("API request failed.")
            return None

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
        return None

    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
        return None

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return None


def install_specific_content_from_servers(
    api_key: str,
    content_version: str,
    pan_hostname: str,
) -> Optional[str]:
    """
    Sends an API request to install the specific content version from the PANW servers.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.
        content_version (str): The version of the content to install.

    Returns:
        Optional[str]: The job ID if the API request is successful, None otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the API request.
    """

    logger.info("=" * 79)
    logger.info(
        f"Attempting to install specific content version: {content_version}"
    )
    logger.info("=" * 79)

    try:
        # Construct the API URL
        url = "https://{}/api/?type=op&cmd={}".format(
            pan_hostname,
            urllib.parse.quote_plus(
                "<request><content><upgrade><install><file>{}</file></install></upgrade></content></request>".format(
                    content_version
                )
            ),
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        request = urllib.request.Request(url)
        request.add_header("X-PAN-KEY", api_key)

        # Send the API request
        logger.debug("Sending API request...")
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )

        # Read the response content
        logger.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logger.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Check the response status
        if root.attrib.get("status") == "success":
            job_element = root.find("./result/job")

            # Extract the job ID from the response
            if job_element is not None:
                job_id = job_element.text
                logger.info("API request successful. Job ID: {}".format(job_id))
                return job_id

            # Log an error if the job ID is not found
            else:
                logger.error("Job ID not found in the response.")
                return None

        else:
            error_message = root.find("./msg/line")
            if error_message is not None:
                logger.error(
                    "API request failed: {}".format(error_message.text)
                )
            else:
                logger.error("API request failed.")
            return None

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
        return None

    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
        return None

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return None


def monitor_job_status(
    api_key: str,
    job_id: str,
    pan_hostname: str,
) -> Optional[bool]:
    """
    Monitors the status of a job on the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.
        job_id (str): The ID of the job to monitor.

    Returns:
        Optional[bool]: True if the job is completed successfully, False otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the job monitoring process.
    """

    logger.info("=" * 79)
    logger.info("Monitoring job status...")
    logger.info("=" * 79)

    start_time = time.time()

    while True:
        try:
            # Construct the API URL for job monitoring
            url = "https://{}/api/?type=op&cmd={}".format(
                pan_hostname,
                urllib.parse.quote_plus(
                    "<show><jobs><id>{}</id></jobs></show>".format(job_id)
                ),
            )
            logger.debug("Job monitoring URL: {}".format(url))

            # Create an HTTPS request with SSL verification disabled
            request = urllib.request.Request(url)
            request.add_header("X-PAN-KEY", api_key)

            # Send the API request
            logger.debug("Sending job monitoring request...")
            response = urllib.request.urlopen(
                request,
                context=urllib.request.ssl._create_unverified_context(),
            )

            # Read the response content
            logger.debug("Reading response content...")
            response_content = response.read().decode("utf-8")
            logger.debug("Received response: {}".format(response_content))

            # Parse the XML response
            logger.debug("Parsing XML response...")
            root = ET.fromstring(response_content)
            logger.debug("Root element: {}".format(root.tag))

            # Check the job status
            job_status_element = root.find("./result/job/status")

            # Check if the job status is FIN
            if job_status_element is not None:
                job_status = job_status_element.text
                if job_status == "FIN":
                    job_result_element = root.find("./result/job/result")

                    # Check the job result
                    if job_result_element is not None:
                        job_result = job_result_element.text
                        if job_result == "OK":
                            logger.info("Job completed successfully.")
                            return True
                        else:
                            logger.error("Job completed with an error.")
                            logger.error(job_result)
                            return False

                    # Log an error if the job result is not found
                    else:
                        logger.error("Job result not found in the response.")
                        return False

            # Check if the job status is ACT
            else:
                logger.error("Job status not found in the response.")
                return False

            # Check the timeout
            if time.time() - start_time > 300:
                logger.error("Job monitoring timed out.")
                return False

            # Wait for 3 seconds before the next iteration
            time.sleep(3)

        except urllib.error.URLError as url_error:
            logger.error("URL error occurred: {}".format(str(url_error)))
        except ET.ParseError as parse_error:
            logger.error(
                "XML parsing error occurred: {}".format(str(parse_error))
            )
        except Exception as e:
            logger.error("An error occurred: {}".format(str(e)))


def private_data_reset(
    api_key: str,
    pan_hostname: str,
) -> bool:
    """
    Resets the configuration data on the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The api key used for authentication.

    Returns:
        Optional[bool]: True if the job is completed successfully, False otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the job monitoring process.
    """

    logger.info("=" * 79)
    logger.info("Resetting the private data...")
    logger.info("=" * 79)

    while True:
        try:
            # Construct the API URL for private data reset
            url = "https://{}/api/?type=op&cmd={}".format(
                pan_hostname,
                urllib.parse.quote_plus(
                    "<request><system><private-data-reset/></system></request>"
                ),
            )
            logger.debug("Request Private Data Reset URL: {}".format(url))

            # Create an HTTPS request with SSL verification disabled
            request = urllib.request.Request(url)
            request.add_header("X-PAN-KEY", api_key)

            # Send the API request
            logger.debug("Sending job monitoring request...")
            response = urllib.request.urlopen(
                request,
                context=urllib.request.ssl._create_unverified_context(),
            )

            # Check the status code
            if response.getcode() != 200:
                raise ValueError(
                    "HTTP request failed with status code: {}".format(
                        response.getcode()
                    )
                )

            # Read the response content
            logger.debug("Reading response content...")
            response_content = response.read().decode("utf-8")
            logger.debug("Received response: {}".format(response_content))

            return True

        except urllib.error.URLError as url_error:
            logger.error("URL error occurred: {}".format(str(url_error)))
            return False

        except ET.ParseError as parse_error:
            logger.error(
                "XML parsing error occurred: {}".format(str(parse_error))
            )
            return False

        except Exception as e:
            logger.error("An error occurred: {}".format(str(e)))
            return False


def retrieve_api_key(
    pan_hostname: str,
    pan_password_new: str,
    pan_username: str,
) -> Optional[str]:
    """
    Retrieves the API key from the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        pan_username (str): The username for authentication.
        pan_password_new (str): The password for authentication.

    Returns:
        Optional[str]: The API key if successfully retrieved, None otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the API request.
    """

    logger.info("=" * 79)
    logger.info("Retrieving API key...")
    logger.info("=" * 79)

    try:
        # Construct the API URL
        url = "https://{}/api/?type=keygen&user={}&password={}".format(
            pan_hostname, pan_username, urllib.parse.quote(pan_password_new)
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        logger.debug("Retrieving API key...")
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )

        # Read the response content
        logger.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logger.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Extract the API key from the response
        logger.debug("Extracting API key...")
        api_key_element = root.find("./result/key")
        if api_key_element is not None:
            api_key = api_key_element.text
            logger.debug("Retrieved API key: {}".format(api_key))
            logger.info("Retrieved API key: {}".format(api_key))
            return api_key
        else:
            logger.error("API key not found in the response.")
            return None

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
        return None

    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
        return None

    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        return None


def retrieve_license(
    api_key: str,
    pan_hostname: str,
) -> Optional[bool]:
    """
    Retrieves the PAN-OS firewall licenses from the CSP.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.

    Returns:
        Optional[bool]: True if the Threat Prevention license is present, False otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response.
        Exception: If any other error occurs during the API request.
    """

    logger.info("=" * 79)
    logger.info("Retrieving licenses...")
    logger.info("=" * 79)

    try:
        # Construct the API URL for retrieving licenses
        url = "https://{}/api/?type=op&cmd={}".format(
            pan_hostname,
            urllib.parse.quote_plus(
                "<request><license><fetch/></license></request>"
            ),
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        request = urllib.request.Request(url)
        request.add_header("X-PAN-KEY", api_key)

        # Send the API request
        logger.debug("Retrieving licenses...")
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )

        # Read the response content
        logger.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logger.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Check the response status
        status = root.attrib.get("status")
        if status == "success":
            # Search for the Threat Prevention license
            threat_prevention_entry = root.find(
                "./result/licenses/entry[feature='Threat Prevention']"
            )
            if threat_prevention_entry is not None:
                logger.info("Threat Prevention license found.")
                return True
            else:
                logger.warning("Threat Prevention license not found.")
                return False
        else:
            logger.error("API request failed.")
            return False

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
    return False
