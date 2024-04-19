# tests/test_private_data_reset.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import private_data_reset


def test_private_data_reset_success():
    """
    Test the private_data_reset function when the API request is successful.

    This test mocks the API response and checks if the function returns True
    when the private data reset request is successful.
    """
    api_key = "api_key"
    pan_hostname = "example.com"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"""
        <response status="success">
            <result>Private data reset successfully</result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen", return_value=mock_response
    ):
        # Call the private_data_reset function
        result = private_data_reset(api_key, pan_hostname)

        # Assert that the function returns True
        assert result is True


def test_private_data_reset_failure():
    """
    Test the private_data_reset function when the API request fails.

    This test mocks the API response with a non-200 status code and checks if
    the function returns False when the private data reset request fails.
    """
    api_key = "api_key"
    pan_hostname = "example.com"

    # Mock the API response with a non-200 status code
    mock_response = MagicMock()
    mock_response.getcode.return_value = 400

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen", return_value=mock_response
    ):
        # Call the private_data_reset function
        result = private_data_reset(api_key, pan_hostname)

        # Assert that the function returns False
        assert result is False


def test_private_data_reset_exception():
    """
    Test the private_data_reset function when an exception occurs.

    This test mocks the urllib.request.urlopen function to raise an exception
    and checks if the function returns False when an exception occurs.
    """
    api_key = "api_key"
    pan_hostname = "example.com"

    # Patch the urllib.request.urlopen function to raise an exception
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        side_effect=Exception("An error occurred"),
    ):
        # Call the private_data_reset function
        result = private_data_reset(api_key, pan_hostname)

        # Assert that the function returns False
        assert result is False
