# tests/test_check_content_version_found.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import reboot_firewall


def test_reboot_firewall_success():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b'<response status="success"/>'

    with patch("urllib.request.urlopen", return_value=mock_response):
        result = reboot_firewall(api_key, pan_hostname)

    assert result is True


def test_reboot_firewall_failure():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.getcode.return_value = 500

    with patch("urllib.request.urlopen", return_value=mock_response):
        result = reboot_firewall(api_key, pan_hostname)

    assert result is False


def test_reboot_firewall_exception():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    with patch(
        "urllib.request.urlopen", side_effect=Exception("Reboot request failed")
    ):
        result = reboot_firewall(api_key, pan_hostname)

    assert result is False
