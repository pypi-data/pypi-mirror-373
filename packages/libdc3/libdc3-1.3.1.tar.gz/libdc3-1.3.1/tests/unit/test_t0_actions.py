from unittest.mock import MagicMock, patch

import pytest

from libdc3.methods.t0_actions import T0Actions


@pytest.fixture
def mock_dc3_config():
    with patch("libdc3.methods.t0_actions.dc3_config") as mock_config:
        mock_config.AUTH_CERT = "fake_cert"
        mock_config.AUTH_CERT_KEY = "fake_key"
        yield mock_config


@pytest.fixture
def mock_t0wm():
    with patch("libdc3.methods.t0_actions.T0WM") as mock_t0wm_cls:
        mock_client = MagicMock()
        mock_t0wm_cls.return_value = mock_client
        yield mock_t0wm_cls


def test_init_calls_validate_x509cert_and_creates_client(mock_dc3_config, mock_t0wm):
    actions = T0Actions()
    mock_dc3_config.validate_x509cert.assert_called_once()
    mock_t0wm.assert_called_with("fake_cert", "fake_key")
    assert isinstance(actions.client, MagicMock)


def test_eras_history_returns_sorted_results(mock_dc3_config, mock_t0wm):
    unsorted_eras = {
        "result": [
            {"era": "B", "data": 2},
            {"era": "A", "data": 1},
            {"era": "C", "data": 3},
        ]
    }
    mock_t0wm.return_value.get_era_history.return_value = unsorted_eras
    actions = T0Actions()
    result = actions.eras_history("some_era")
    assert result == [
        {"era": "A", "data": 1},
        {"era": "B", "data": 2},
        {"era": "C", "data": 3},
    ]
    mock_t0wm.return_value.get_era_history.assert_called_once_with(era="some_era")


def test_eras_history_empty_result(mock_dc3_config, mock_t0wm):
    mock_t0wm.return_value.get_era_history.return_value = {"result": []}
    actions = T0Actions()
    result = actions.eras_history("no_era")
    assert result == []
    mock_t0wm.return_value.get_era_history.assert_called_once_with(era="no_era")
