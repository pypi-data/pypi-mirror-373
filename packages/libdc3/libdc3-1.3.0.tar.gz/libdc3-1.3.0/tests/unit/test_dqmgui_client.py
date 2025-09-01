from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import SSLError

from libdc3.services.dqmgui.client import DQMGUI


@pytest.fixture
def dqmgui():
    return DQMGUI(cert="cert.pem", key="key.pem", timeout=10)


@patch("libdc3.services.dqmgui.client.requests.get")
def test_get_samples_success(mock_get, dqmgui):
    mock_response = MagicMock()
    mock_response.json.return_value = {"samples": [{"items": [{"run": "123"}]}]}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = dqmgui.get_samples("dataset", "123")
    assert result == {"samples": [{"items": [{"run": "123"}]}]}
    mock_get.assert_called_once()


@patch("libdc3.services.dqmgui.client.requests.get")
def test_get_samples_ssl_error_fallback(mock_get, dqmgui):
    # First call raises SSLError, second returns mock response
    mock_get.side_effect = [SSLError("SSL error"), MagicMock()]
    mock_response = MagicMock()
    mock_response.json.return_value = {"samples": []}
    mock_response.raise_for_status.return_value = None
    mock_get.side_effect = [SSLError("SSL error"), mock_response]

    with patch("libdc3.services.dqmgui.client.urllib3.disable_warnings"):
        result = dqmgui.get_samples("dataset", "456")
    assert result == {"samples": []}
    assert mock_get.call_count == 2


@patch.object(DQMGUI, "get_samples")
def test_check_if_runs_are_present_some_missing(mock_get_samples, dqmgui):
    # Only run 2 is present in GUI
    mock_get_samples.return_value = {"samples": [{"items": [{"run": "2"}]}]}
    missing = dqmgui.check_if_runs_are_present("dataset", [1, 2, 3])
    assert missing == [1, 3]


@patch.object(DQMGUI, "get_samples")
def test_check_if_runs_are_present_all_present(mock_get_samples, dqmgui):
    mock_get_samples.return_value = {"samples": [{"items": [{"run": "1"}, {"run": "2"}, {"run": "3"}]}]}
    missing = dqmgui.check_if_runs_are_present("dataset", [1, 2, 3])
    assert missing == []


@patch.object(DQMGUI, "get_samples")
def test_check_if_runs_are_present_none_present(mock_get_samples, dqmgui):
    mock_get_samples.return_value = {"samples": []}
    missing = dqmgui.check_if_runs_are_present("dataset", [10, 20])
    assert missing == [10, 20]
