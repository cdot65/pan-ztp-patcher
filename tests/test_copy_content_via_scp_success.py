# tests/test_copy_content_via_scp_success.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import copy_content_via_scp
from paramiko import SSHException


# def test_copy_content_via_scp_success():
#     """
#     Test the copy_content_via_scp function when the SCP import is successful.

#     This test mocks the SSH session and simulates a successful SCP import.
#     It checks if the function returns True when the import is completed successfully.
#     """
#     content_path = "/path/to/content"
#     content_version = "content_version"
#     pan_hostname = "example.com"
#     pan_password_new = "newpassword"
#     pan_username = "admin"
#     pi_hostname = "raspberrypi.local"
#     pi_password = "raspberry"
#     pi_username = "pi"

#     # Mock the paramiko.SSHClient and its methods
#     with patch("pan_ztp_patcher.ztp_patcher.paramiko.SSHClient") as mock_ssh_client:
#         mock_client = MagicMock()
#         mock_ssh_client.return_value = mock_client

#         mock_shell = MagicMock()
#         mock_client.invoke_shell.return_value = mock_shell

#         # Mock the shell.recv method to return the expected prompts and messages
#         mock_shell.recv.side_effect = [
#             b"PA-450>",
#             b"raspberrypi.local...",
#             b"Warning: Permanently added 'raspberrypi.local' (ECDSA) to the list of known hosts.",
#             b"pi@raspberrypi.local's password:",
#             b"content_version             100%   10MB   1.0MB/s   00:10\r\n",
#             b"SCP import content job succeeded.",
#             b"PA-450>",
#         ]

#         # Call the copy_content_via_scp function
#         result = copy_content_via_scp(
#             content_path,
#             content_version,
#             pan_hostname,
#             pan_password_new,
#             pan_username,
#             pi_hostname,
#             pi_password,
#             pi_username,
#         )

#         # Assert that the function returns True
#         assert result is True
#         mock_client.connect.assert_called_once_with(
#             hostname=pan_hostname,
#             username=pan_username,
#             password=pan_password_new,
#         )
#         mock_client.invoke_shell.assert_called_once()
#         mock_client.close.assert_called_once()


def test_copy_content_via_scp_failure_ssh_exception():
    """
    Test the copy_content_via_scp function when an SSH exception occurs.

    This test mocks the SSH session and simulates an SSH exception.
    It checks if the function returns False when an SSH exception occurs.
    """
    content_path = "/path/to/content"
    content_version = "content_version"
    pan_hostname = "example.com"
    pan_password_new = "newpassword"
    pan_username = "admin"
    pi_hostname = "raspberrypi.local"
    pi_password = "raspberry"
    pi_username = "pi"

    # Mock the paramiko.SSHClient and its methods
    with patch("pan_ztp_patcher.ztp_patcher.paramiko.SSHClient") as mock_ssh_client:
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client

        # Mock the invoke_shell method to raise an SSHException
        mock_client.invoke_shell.side_effect = SSHException("SSH exception occurred")

        # Call the copy_content_via_scp function
        result = copy_content_via_scp(
            content_path,
            content_version,
            pan_hostname,
            pan_password_new,
            pan_username,
            pi_hostname,
            pi_password,
            pi_username,
        )

        # Assert that the function returns False
        assert result is False
        mock_client.connect.assert_called_once_with(
            hostname=pan_hostname,
            username=pan_username,
            password=pan_password_new,
        )
        mock_client.invoke_shell.assert_called_once()
        mock_client.close.assert_not_called()


# def test_copy_content_via_scp_failure_timeout():
#     """
#     Test the copy_content_via_scp function when a timeout occurs.

#     This test mocks the SSH session and simulates a timeout scenario.
#     It checks if the function returns False when a timeout occurs.
#     """
#     content_path = "/path/to/content"
#     content_version = "content_version"
#     pan_hostname = "example.com"
#     pan_password_new = "newpassword"
#     pan_username = "admin"
#     pi_hostname = "raspberrypi.local"
#     pi_password = "raspberry"
#     pi_username = "pi"

#     # Mock the paramiko.SSHClient and its methods
#     with patch("pan_ztp_patcher.ztp_patcher.paramiko.SSHClient") as mock_ssh_client:
#         mock_client = MagicMock()
#         mock_ssh_client.return_value = mock_client

#         mock_shell = MagicMock()
#         mock_client.invoke_shell.return_value = mock_shell

#         # Mock the shell.recv method to simulate a timeout
#         mock_shell.recv.side_effect = [b"PA-450>"]

#         # Call the copy_content_via_scp function
#         result = copy_content_via_scp(
#             content_path,
#             content_version,
#             pan_hostname,
#             pan_password_new,
#             pan_username,
#             pi_hostname,
#             pi_password,
#             pi_username,
#         )

#         # Assert that the function returns False
#         assert result is False
#         mock_client.connect.assert_called_once_with(
#             hostname=pan_hostname,
#             username=pan_username,
#             password=pan_password_new,
#         )
#         mock_client.invoke_shell.assert_called_once()
#         mock_client.close.assert_called_once()
