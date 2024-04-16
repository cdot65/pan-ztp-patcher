import logging
import paramiko
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

from pan_ztp_patcher.constants import (
    MONITOR_JOB_STATUS_TIMEOUT,
    SCP_IMPORT_TIMEOUT,
)  # noqa: E501


logger = logging.getLogger(__name__)


def change_firewall_password(
    pan_hostname,
    pan_username,
    pan_password,
    pan_password_default,
):
    """
    Changes the password of a user on the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        pan_username (str): The username for authentication.
        pan_password (str): The new password to set for the user.
        pan_password_default (str): The current password of the user.

    Returns:
        None

    Raises:
        paramiko.AuthenticationException: If authentication fails.
        paramiko.SSHException: If an SSH exception occurs.
        Exception: If any other error occurs during the password change process. # noqa: E501

    Example:
        change_firewall_password("192.168.1.1", "admin", "pan_password_default", "pan_password")
    """

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the firewall
        logging.debug("Connecting to {}...".format(pan_hostname))
        client.connect(
            pan_hostname, username=pan_username, password=pan_password_default
        )
        logger.info("Connected to {} successfully.".format(pan_hostname))

        # Create an interactive shell
        shell = client.invoke_shell()

        # Wait for the prompt
        logging.debug("Waiting for the prompt...")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the old password
        logger.debug(
            "Sending pan_password_default: {}".format(pan_password_default)
        )  # noqa: E501
        shell.send(pan_password_default + "\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the new password
        logger.debug("Sending pan_password: {}".format(pan_password))
        shell.send(pan_password + "\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Confirm the new password
        logger.debug("Confirming pan_password: {}".format(pan_password))
        shell.send(pan_password + "\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Close the SSH connection
        logging.debug("Closing the SSH connection...")
        client.close()
        logger.info("Password changed successfully.")

    except paramiko.AuthenticationException:
        logger.error("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as ssh_exception:
        logger.error("SSH exception occurred: {}".format(str(ssh_exception)))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))


def retrieve_api_key(
    pan_hostname,
    pan_username,
    pan_password,
):
    """
    Retrieves the API key from the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        pan_username (str): The username for authentication.
        pan_password (str): The password for authentication.

    Returns:
        str: The API key if successfully retrieved, None otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response. # noqa: E501
        Exception: If any other error occurs during the API request.

    Example:
        api_key = retrieve_api_key("192.168.1.1", "admin", "password")
    """

    try:
        # Construct the API URL
        url = "https://{}/api/?type=keygen&user={}&password={}".format(
            pan_hostname, pan_username, urllib.parse.quote(pan_password)
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        logging.debug("Retrieving API key...")
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )
        logging.debug("Received response: {}".format(response))

        # Read the response content
        logging.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logging.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Extract the API key from the response
        logging.debug("Extracting API key...")
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
    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
    return None


def import_content_via_scp(
    pan_hostname,
    pan_username,
    pan_password,
    pi_hostname,
    pi_username,
    pi_password,
    content_path,
    content_file,
):
    """
    Imports content to the PAN-OS firewall using SCP.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        pan_username (str): The username for authentication.
        pan_password (str): The password for authentication.
        pi_hostname (str): The hostname or IP address of the Raspberry Pi.
        pi_content_path (str): The path to the content file on the Raspberry Pi.
        content_file (str): The name of the content file.

    Returns:
        None

    Raises:
        paramiko.AuthenticationException: If authentication fails.
        paramiko.SSHException: If an SSH exception occurs.
        Exception: If any other error occurs during the SCP import process.

    Example:
        import_content_via_scp("192.168.1.1", "admin", "password", "192.168.1.2", "/var/tmp/", "content.txt") # noqa: E501
    """

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the firewall
        logger.debug("Connecting to {}...".format(pan_hostname))
        client.connect(
            pan_hostname, username=pan_username, password=pan_password
        )  # noqa: E501
        logger.info("Connected to {} successfully.".format(pan_hostname))

        # Create an interactive shell
        shell = client.invoke_shell()

        # Wait for the prompt
        logger.debug("Waiting for the prompt...")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the scp import command
        scp_command = "scp import content from {}@{}:{}/{}".format(
            pi_username,
            pi_hostname,
            content_path,
            content_file,
        )
        logger.debug("Sending SCP command: {}".format(scp_command))
        shell.send(scp_command + "\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Check if the host authenticity prompt appears
        logging.debug("Checking for host authenticity prompt...")
        if "Are you sure you want to continue connecting" in output:
            logger.debug("Sending 'yes' to the prompt...")
            shell.send("yes\n")
            time.sleep(2)
            output = shell.recv(1024).decode("utf-8")
            logger.debug("Received output: {}".format(output))

        # Send the password for pi@
        logging.debug("Sending password for pi@{}...".format(pi_hostname))
        shell.send(pi_password + "\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Wait for the completion prompt
        logger.debug("Waiting for the completion prompt...")
        start_time = time.time()
        while "saved" not in output:
            if time.time() - start_time > SCP_IMPORT_TIMEOUT:
                logger.error(
                    "Timeout occurred while waiting for the completion prompt."
                )
                break
            output += shell.recv(1024).decode("utf-8")
            logger.debug("Received output: {}".format(output))
            time.sleep(1)

        logger.debug("SCP import content completed successfully.")
        logger.info("SCP import content completed successfully.")

        # Close the SSH connection
        client.close()

    except paramiko.AuthenticationException:
        logger.error("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as ssh_exception:
        logger.error("SSH exception occurred: {}".format(str(ssh_exception)))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))


def install_content_via_api(
    pan_hostname,
    api_key,
    content_file,
):
    """
    Sends an API request to install the content on the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.
        content_file (str): The name of the content file to install.

    Returns:
        str: The job ID if the API request is successful, None otherwise.

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response. # noqa: E501
        Exception: If any other error occurs during the API request.

    Example:
        job_id = install_content_via_api("192.168.1.1", "api_key", "content.txt")
    """

    try:
        # Construct the API URL
        url = "https://{}/api/?type=op&cmd={}".format(
            pan_hostname,
            urllib.parse.quote_plus(
                "<request><content><upgrade><install><file>{}</file></install></upgrade></content></request>".format(  # noqa: E501
                    content_file
                )
            ),
        )
        logger.debug("API URL: {}".format(url))

        # Create an HTTPS request with SSL verification disabled
        request = urllib.request.Request(url)
        request.add_header("X-PAN-KEY", api_key)

        # Send the API request
        logging.debug("Sending API request...")
        response = urllib.request.urlopen(
            request, context=urllib.request.ssl._create_unverified_context()
        )
        logging.debug("Received response: {}".format(response))

        # Read the response content
        logging.debug("Reading response content...")
        response_content = response.read().decode("utf-8")
        logger.debug("Received response: {}".format(response_content))

        # Parse the XML response
        logging.debug("Parsing XML response...")
        root = ET.fromstring(response_content)
        logger.debug("Root element: {}".format(root.tag))

        # Check the response status
        status = root.attrib.get("status")
        if status == "success":
            job_element = root.find("./result/job")
            if job_element is not None:
                job_id = job_element.text
                logger.info(
                    "API request successful. Job ID: {}".format(job_id)
                )  # noqa: E501
                return job_id
            else:
                logger.error("Job ID not found in the response.")
                return None
        else:
            logger.error("API request failed.")
            return None

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))


def monitor_job_status(pan_hostname, api_key, job_id):
    """
    Monitors the status of a job on the PAN-OS firewall.

    Args:
        pan_hostname (str): The hostname or IP address of the PAN-OS firewall.
        api_key (str): The API key for authentication.
        job_id (str): The ID of the job to monitor.

    Returns:
        None

    Raises:
        urllib.error.URLError: If a URL error occurs during the API request.
        xml.etree.ElementTree.ParseError: If an error occurs while parsing the XML response. # noqa: E501
        Exception: If any other error occurs during the job monitoring process.

    Example:
        monitor_job_status("192.168.1.1", "api_key", "job_id")
    """

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
            logging.debug("Sending job monitoring request...")
            response = urllib.request.urlopen(
                request,
                context=urllib.request.ssl._create_unverified_context(),  # noqa: E501
            )
            logging.debug("Received response: {}".format(response))

            # Read the response content
            logging.debug("Reading response content...")
            response_content = response.read().decode("utf-8")
            logger.debug("Received response: {}".format(response_content))

            # Parse the XML response
            logging.debug("Parsing XML response...")
            root = ET.fromstring(response_content)
            logger.debug("Root element: {}".format(root.tag))

            # Check the job status
            job_status_element = root.find("./result/job/status")
            if job_status_element is not None:
                job_status = job_status_element.text
                if job_status == "FIN":
                    job_result_element = root.find("./result/job/result")
                    if job_result_element is not None:
                        job_result = job_result_element.text
                        if job_result == "OK":
                            logger.info("Job completed successfully.")
                            return
                        else:
                            logger.error("Job completed with an error.")
                            sys.exit(1)
                    else:
                        logger.error("Job result not found in the response.")
                        sys.exit(1)
            else:
                logger.error("Job status not found in the response.")
                sys.exit(1)

            # Check the timeout
            if time.time() - start_time > MONITOR_JOB_STATUS_TIMEOUT:
                logger.error("Job monitoring timed out.")
                sys.exit(1)

            # Wait for 2 seconds before the next iteration
            time.sleep(2)

        except urllib.error.URLError as url_error:
            logger.error("URL error occurred: {}".format(str(url_error)))
        except ET.ParseError as parse_error:
            logger.error(
                "XML parsing error occurred: {}".format(str(parse_error))
            )  # noqa: E501
        except Exception as e:
            logger.error("An error occurred: {}".format(str(e)))
