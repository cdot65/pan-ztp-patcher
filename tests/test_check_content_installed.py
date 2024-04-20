# tests/test_check_content_installed.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import check_content_installed


def test_check_content_installed_success():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b'<response status="success"><result><job>1234</job></result></response>'

    with patch("urllib.request.urlopen", return_value=mock_response):
        job_id = check_content_installed(
            api_key,
            pan_hostname,
        )

    assert job_id == "1234"


def test_check_content_installed_failure():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b'<response status="error"><msg><line>API request failed</line></msg></response>'

    with patch("urllib.request.urlopen", return_value=mock_response):
        job_id = check_content_installed(
            api_key,
            pan_hostname,
        )

    assert job_id is None


def test_check_content_installed_exception():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    with patch(
        "urllib.request.urlopen", side_effect=Exception("API request failed")
    ):
        job_id = check_content_installed(
            api_key,
            pan_hostname,
        )

    assert job_id is None
