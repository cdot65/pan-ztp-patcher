# tests/test_retrieve_license.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import retrieve_license


def test_retrieve_license_success():
    """
    Test the retrieve_license function when the Threat Prevention license is present.

    This test mocks the API response with the Threat Prevention license entry and
    checks if the function returns True when the license is found.
    """
    api_key = "api_key"
    pan_hostname = "example.com"

    # Mock the API response with the Threat Prevention license entry
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="success">
            <result>
                <licenses>
                    <entry>
                        <feature>Threat Prevention</feature>
                        <expires>Never</expires>
                    </entry>
                </licenses>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        return_value=mock_response,
    ):
        # Call the retrieve_license function
        result = retrieve_license(api_key, pan_hostname)

        # Assert that the function returns True
        assert result is True


def test_retrieve_license_failure():
    """
    Test the retrieve_license function when the Threat Prevention license is not present.

    This test mocks the API response without the Threat Prevention license entry and
    checks if the function returns False when the license is not found.
    """
    api_key = "api_key"
    pan_hostname = "example.com"

    # Mock the API response without the Threat Prevention license entry
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="success">
            <result>
                <licenses>
                    <entry>
                        <feature>Other License</feature>
                        <expires>Never</expires>
                    </entry>
                </licenses>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        return_value=mock_response,
    ):
        # Call the retrieve_license function
        result = retrieve_license(api_key, pan_hostname)

        # Assert that the function returns False
        assert result is False


def test_retrieve_license_api_failure():
    """
    Test the retrieve_license function when the API request fails.

    This test mocks the API response with an error status and checks if the function
    returns False when the API request fails.
    """
    api_key = "api_key"
    pan_hostname = "example.com"

    # Mock the API response with an error status
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="error">
            <result>
                <msg>API request failed</msg>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        return_value=mock_response,
    ):
        # Call the retrieve_license function
        result = retrieve_license(api_key, pan_hostname)

        # Assert that the function returns False
        assert result is False


def test_retrieve_license_exception():
    """
    Test the retrieve_license function when an exception occurs.

    This test mocks the urllib.request.urlopen function to raise an exception and
    checks if the function returns False when an exception occurs.
    """
    api_key = "api_key"
    pan_hostname = "example.com"

    # Patch the urllib.request.urlopen function to raise an exception
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen",
        side_effect=Exception("An error occurred"),
    ):
        # Call the retrieve_license function
        result = retrieve_license(api_key, pan_hostname)

        # Assert that the function returns False
        assert result is False
