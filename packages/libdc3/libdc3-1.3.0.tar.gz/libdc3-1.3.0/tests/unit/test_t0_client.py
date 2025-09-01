from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import SSLError

from libdc3.services.t0.client import T0WM


@pytest.fixture
def t0wm():
    return T0WM(cert="cert.pem", key="key.pem", timeout=10)


@patch("libdc3.services.t0.client.requests.get")
def test_get_era_history_success(mock_get, t0wm):
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = t0wm.get_era_history("TestEra")
    mock_get.assert_called_once_with(
        t0wm.T0_URL + "/era_history",
        params={"era": "TestEra"},
        cert=("cert.pem", "key.pem"),
        timeout=10,
    )
    assert result == {"result": "ok"}


@patch("libdc3.services.t0.client.requests.get")
def test_get_era_history_raises_for_status(mock_get, t0wm):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP error")
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="HTTP error"):
        t0wm.get_era_history("TestEra")


@patch("libdc3.services.t0.client.requests.get")
def test_get_era_history_ssl_error_triggers_insecure(mock_get, t0wm):
    # First call raises SSLError, second call returns a valid response
    def side_effect(*args, **kwargs):
        if kwargs.get("verify", True):
            raise SSLError("SSL error")
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status.return_value = None
        return mock_response

    mock_get.side_effect = side_effect

    with patch("libdc3.services.t0.client.urllib3.disable_warnings") as mock_disable_warnings:
        result = t0wm.get_era_history("TestEra")
        assert result == {"result": "ok"}
        assert mock_get.call_count == 2
        # Second call should have verify=False
        _, kwargs = mock_get.call_args
        assert kwargs["verify"] is False
        mock_disable_warnings.assert_called_once()


@patch("libdc3.services.t0.client.requests.get")
def test_get_era_history_ssl_error_and_http_error(mock_get, t0wm):
    # First call raises SSLError, second call raises HTTP error
    def side_effect(*args, **kwargs):
        if kwargs.get("verify", True):
            raise SSLError("SSL error")
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP error")
        return mock_response

    mock_get.side_effect = side_effect

    with pytest.raises(Exception, match="HTTP error"):
        t0wm.get_era_history("TestEra")
