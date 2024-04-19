# tests/test_download_software.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import download_software


def test_download_software_success():
    """
    Test the download_software function when the API request is successful.

    This test mocks the API response and checks if the function returns the job ID
    when the download request is successful.
    """
    api_key = "api_key"
    content_version = "content_version"
    pan_hostname = "example.com"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="success">
            <result>
                <job>123456</job>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        return_value=mock_response,
    ):
        # Call the download_software function
        job_id = download_software(api_key, content_version, pan_hostname)

        # Assert that the function returns the expected job ID
        assert job_id == "123456"


def test_download_software_failure():
    """
    Test the download_software function when the API request fails.

    This test mocks the API response with an error status and checks if the function
    returns None when the download request fails.
    """
    api_key = "api_key"
    content_version = "content_version"
    pan_hostname = "example.com"

    # Mock the API response with an error status
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="error">
            <msg>
                <line>An error occurred</line>
            </msg>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        return_value=mock_response,
    ):
        # Call the download_software function
        job_id = download_software(api_key, content_version, pan_hostname)

        # Assert that the function returns None
        assert job_id is None


def test_download_software_exception():
    """
    Test the download_software function when an exception occurs.

    This test mocks the urllib.request.urlopen function to raise an exception and
    checks if the function returns None when an exception occurs.
    """
    api_key = "api_key"
    content_version = "content_version"
    pan_hostname = "example.com"

    # Patch the urllib.request.urlopen function to raise an exception
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        side_effect=Exception("An error occurred"),
    ):
        # Call the download_software function
        job_id = download_software(api_key, content_version, pan_hostname)

        # Assert that the function returns None
        assert job_id is None
