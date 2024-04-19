# tests/test_monitor_job_status.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import monitor_job_status


def test_monitor_job_status_success():
    """
    Test the monitor_job_status function when the job is completed successfully.

    This test mocks the API response and checks if the function returns True
    when the job is completed with a status of "OK".
    """
    api_key = "api_key"
    job_id = "123456"
    pan_hostname = "example.com"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="success">
            <result>
                <job>
                    <status>FIN</status>
                    <result>OK</result>
                </job>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen", return_value=mock_response
    ):
        # Call the monitor_job_status function
        result = monitor_job_status(
            api_key,
            job_id,
            pan_hostname,
        )

        # Assert that the function returns True
        assert result is True


def test_monitor_job_status_failure():
    """
    Test the monitor_job_status function when the job is completed with an error.

    This test mocks the API response and checks if the function returns False
    when the job is completed with an error status.
    """
    api_key = "api_key"
    job_id = "123456"
    pan_hostname = "example.com"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b"""
        <response status="success">
            <result>
                <job>
                    <status>FIN</status>
                    <result>Error</result>
                </job>
            </result>
        </response>
    """

    # Patch the urllib.request.urlopen function
    with patch(
        "pan_ztp_patcher.ztp_patcher.urllib.request.urlopen", return_value=mock_response
    ):
        # Call the monitor_job_status function
        result = monitor_job_status(
            api_key,
            job_id,
            pan_hostname,
        )

        # Assert that the function returns False
        assert result is False
