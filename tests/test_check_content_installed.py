# tests/test_check_content_installed.py

from unittest.mock import MagicMock, patch
from pan_ztp_patcher.ztp_patcher import check_content_installed


def test_check_content_installed_success():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b'<response status="success"><result><content-updates last-updated-at="2024/04/20 04:10:01 PDT"><entry><version>8831-8669</version><app-version>8831-8669</app-version><filename>panupv2-all-contents-8831-8669</filename><size>86</size><size-kb>89019</size-kb><released-on>2024/04/08 13:28:31 PDT</released-on><release-notes><![CDATA[https://proditpdownloads.paloaltonetworks.com/content/content-8831-8669.html?__token__=exp=1714216359~acl=/content/content-8831-8669.html*~hmac=e9aaf43c583e2902e708bc3be0d6511f189b5f25580110280054eb5b03e3bbda]]></release-notes><downloaded>yes</downloaded><current>yes</current><previous>no</previous><installing>no</installing><features>Apps, Threats</features><update-type>Full</update-type><feature-desc>Unknown</feature-desc><sha256>ae12ea7da3a05927943c7de3f3441e31d3f1020902a9c9e63885ddf060d84e4d</sha256></entry></content-updates></result></response>'

    with patch(
        "urllib.request.urlopen",
        return_value=mock_response,
    ):
        content_installed = check_content_installed(
            api_key,
            pan_hostname,
        )

    assert content_installed is True


def test_check_content_installed_failure():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    # Mock the API response
    mock_response = MagicMock()
    mock_response.read.return_value = b'<response status="error"><msg><line>API request failed</line></msg></response>'

    with patch("urllib.request.urlopen", return_value=mock_response):
        content_installed = check_content_installed(
            api_key,
            pan_hostname,
        )

    assert content_installed is False


def test_check_content_installed_exception():
    api_key = "your_api_key"
    pan_hostname = "your_pan_hostname"

    with patch(
        "urllib.request.urlopen", side_effect=Exception("API request failed")
    ):
        content_installed = check_content_installed(
            api_key,
            pan_hostname,
        )

    assert content_installed is False
