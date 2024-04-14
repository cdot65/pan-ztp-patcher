import logging
import paramiko
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET


logger = logging.getLogger(__name__)


def change_password(hostname, username, old_password, new_password):
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the firewall
        logging.debug("Connecting to {}...".format(hostname))
        client.connect(hostname, username=username, password=old_password)
        logger.info("Connected to {} successfully.".format(hostname))

        # Create an interactive shell
        shell = client.invoke_shell()

        # Wait for the prompt
        logging.debug("Waiting for the prompt...")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the old password
        logger.debug("Sending old_password: {}".format(old_password))
        shell.send(old_password + "\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the new password
        logger.debug("Sending new_password: {}".format(new_password))
        shell.send(new_password + "\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Confirm the new password
        logger.debug("Confirming new_password: {}".format(new_password))
        shell.send(new_password + "\n")
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


def get_api_key(hostname, username, password):
    try:
        # Construct the API URL
        url = "https://{}/api/?type=keygen&user={}&password={}".format(
            hostname, username, urllib.parse.quote(password)
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
        api_key = root.find("./result/key").text
        logger.debug("Retrieved API key: {}".format(api_key))
        logger.info("Retrieved API key: {}".format(api_key))

        return api_key

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
    return None


def scp_import_content(
    hostname,
    username,
    password,
    pi_hostname,
    pi_content_path,
    content_file,
):
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the firewall
        logger.debug("Connecting to {}...".format(hostname))
        client.connect(hostname, username=username, password=password)
        logger.info("Connected to {} successfully.".format(hostname))

        # Create an interactive shell
        shell = client.invoke_shell()

        # Wait for the prompt
        logger.debug("Waiting for the prompt...")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Send the scp import command
        scp_command = "scp import content from pi@{}:{}/{}".format(
            pi_hostname,
            pi_content_path,
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

        # Send the password for pi@192.168.1.2
        logger.debug("Sending password for pi@{}...".format(pi_hostname))
        time.sleep(2)

        # Send the password for pi@
        logging.debug("Sending password for pi@{}...".format(pi_hostname))
        shell.send("paloalto123\n")
        time.sleep(2)
        output = shell.recv(1024).decode("utf-8")
        logger.debug("Received output: {}".format(output))

        # Wait for the completion prompt
        logger.debug("Waiting for the completion prompt...")
        timeout = 30  # Increase the timeout to 30 seconds or adjust as needed
        start_time = time.time()
        while "saved" not in output:
            if time.time() - start_time > timeout:
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


def send_api_request(hostname, api_key, content_file):
    try:
        # Construct the API URL
        url = "https://{}/api/?type=op&cmd={}".format(
            hostname,
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
            job_id = root.find("./result/job").text
            logger.info("API request successful. Job ID: {}".format(job_id))
            return job_id
        else:
            logger.error("API request failed.")
            return None

    except urllib.error.URLError as url_error:
        logger.error("URL error occurred: {}".format(str(url_error)))
    except ET.ParseError as parse_error:
        logger.error("XML parsing error occurred: {}".format(str(parse_error)))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))


def job_monitor(hostname, api_key, job_id):
    start_time = time.time()
    timeout = 30

    while True:
        try:
            # Construct the API URL for job monitoring
            url = "https://{}/api/?type=op&cmd={}".format(
                hostname,
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
            job_status = root.find("./result/job/status").text
            if job_status == "FIN":
                job_result = root.find("./result/job/result").text
                if job_result == "OK":
                    logger.info("Job completed successfully.")
                    return
                else:
                    logger.error("Job completed with an error.")
                    sys.exit(1)

            # Check the timeout
            if time.time() - start_time > timeout:
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
