# tests/test_ztp_patcher.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import change_firewall_password


def test_change_firewall_password():
    """
    Test the change_firewall_password function.

    This test mocks the necessary inputs and checks if the function returns True
    when the password change is successful and the expected warning message is received.
    """
    pan_hostname = "example.com"
    pan_password_new = "newpassword"
    pan_password_old = "oldpassword"
    pan_username = "admin"

    # Mock the paramiko.SSHClient and its methods
    with patch("pan_ztp_patcher.ztp_patcher.paramiko.SSHClient") as mock_ssh_client:
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client

        mock_shell = MagicMock()
        mock_client.invoke_shell.return_value = mock_shell

        # Mock the shell.recv method to return the expected prompts and messages
        mock_shell.recv.side_effect = [
            b"PA-450 login:",
            b"Password:",
            b"Enter old password:",
            b"New password:",
            b"Confirm password:",
            b"Warning: Your device is still configured with the default admin account credentials. Please change your password prior to deployment.",
        ]

        # Call the change_firewall_password function
        result = change_firewall_password(
            pan_hostname,
            pan_password_new,
            pan_password_old,
            pan_username,
        )

        # Assert that the function returns True and the expected methods were called with the correct arguments
        assert result is True
        mock_client.connect.assert_called_once_with(
            hostname=pan_hostname,
            username=pan_username,
            password=pan_password_old,
        )
        mock_client.invoke_shell.assert_called_once()
        assert mock_shell.send.call_count == 3
        mock_shell.send.assert_any_call(pan_password_old + "\n")
        mock_shell.send.assert_any_call(pan_password_new + "\n")
        mock_shell.send.assert_any_call(pan_password_new + "\n")
        mock_client.close.assert_called_once()
