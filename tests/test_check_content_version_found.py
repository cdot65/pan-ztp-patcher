# tests/test_check_content_version_found.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import check_content_version


def test_check_content_version_found():
    """
    Test the check_content_version function when the content version is found.

    This test mocks the API response and checks if the function returns True
    when the specified content version is found in the response.
    """
    api_key = "api_key"
    content_version = "content_version"
    pan_hostname = "example.com"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="success">
            <result>
                <entry>
                    <filename>content_version</filename>
                </entry>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        return_value=mock_response,
    ):
        result = check_content_version(
            api_key,
            content_version,
            pan_hostname,
        )
        assert result is True


def test_check_content_version_not_found():
    """
    Test the check_content_version function when the content version is not found.

    This test mocks the API response and checks if the function returns False
    when the specified content version is not found in the response.
    """
    api_key = "api_key"
    content_version = "content_version"
    pan_hostname = "example.com"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="success">
            <result>
                <entry>
                    <filename>different_content_version</filename>
                </entry>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        return_value=mock_response,
    ):
        result = check_content_version(
            api_key,
            content_version,
            pan_hostname,
        )
        assert result is False
