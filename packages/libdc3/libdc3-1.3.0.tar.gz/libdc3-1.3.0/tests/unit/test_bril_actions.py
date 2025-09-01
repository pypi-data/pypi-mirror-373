from datetime import datetime
from unittest.mock import patch

import pytest

from libdc3.methods.bril_actions import BrilActions


@pytest.fixture
def bril_actions():
    return BrilActions(
        brilws_version="3.7.4",
        unit="/ub",
        low_lumi_thr=80000.0,
        beamstatus="STABLE BEAMS",
        amodetag="PROTPHYS",
        normtag="test_normtag",
    )


@patch("libdc3.methods.bril_actions.Brilcalc")
@patch("libdc3.methods.bril_actions.dc3_config")
def test_fetch_lumis_run_number(mock_config, mock_brilcalc, bril_actions):
    # Mock config
    mock_config.KEYTAB_USR = "user"
    mock_config.KEYTAB_PWD = "pwd"
    # Mock Brilcalc.lumi return value
    mock_brilcalc.return_value.lumi.return_value = {
        "detailed": [
            {
                "run": 123,
                "ls_number": 1,
                "time": "01/01/24 12:00:00",
                "delivered(/ub)": 5.0,
                "recorded(/ub)": 4.5,
            },
            {
                "run": 123,
                "ls_number": 2,
                "time": "01/01/24 12:01:00",
                "delivered(/ub)": 6.0,
                "recorded(/ub)": 5.5,
            },
        ]
    }
    lumis = bril_actions.fetch_lumis(run_number=123)
    assert "detailed" in lumis
    assert lumis["detailed"][0]["run_number"] == 123
    assert isinstance(lumis["detailed"][0]["datetime"], datetime)
    assert pytest.approx(lumis["detailed"][0]["delivered"]) == 5.0
    assert pytest.approx(lumis["detailed"][0]["recorded"]) == 4.5


@patch("libdc3.methods.bril_actions.Brilcalc")
@patch("libdc3.methods.bril_actions.dc3_config")
def test_fetch_lumis_begin_end(mock_config, mock_brilcalc, bril_actions):
    mock_config.KEYTAB_USR = "user"
    mock_config.KEYTAB_PWD = "pwd"
    mock_brilcalc.return_value.lumi.return_value = {
        "detailed": [
            {
                "run": 124,
                "ls_number": 1,
                "time": "01/02/24 13:00:00",
                "delivered(/ub)": 7.0,
                "recorded(/ub)": 6.5,
            }
        ]
    }
    lumis = bril_actions.fetch_lumis(begin="2024-01-02", end="2024-01-03")
    assert lumis["detailed"][0]["run_number"] == 124
    assert pytest.approx(lumis["detailed"][0]["delivered"]) == 7.0


def test_fetch_lumis_invalid_args(bril_actions):
    with pytest.raises(ValueError):
        bril_actions.fetch_lumis()
    with pytest.raises(ValueError):
        bril_actions.fetch_lumis(begin="2024-01-01")
    with pytest.raises(ValueError):
        bril_actions.fetch_lumis(end="2024-01-01")


def test_agg_by_run(bril_actions):
    bril_detailed = [
        {"run_number": 100, "delivered": 2.0, "recorded": 1.0},
        {"run_number": 100, "delivered": 3.0, "recorded": 2.0},
        {"run_number": 101, "delivered": 5.0, "recorded": 12.0},
    ]
    result = bril_actions.agg_by_run(bril_detailed)
    assert len(result) == 2
    run_100 = next(r for r in result if r["run_number"] == 100)
    run_101 = next(r for r in result if r["run_number"] == 101)
    assert pytest.approx(run_100["delivered"]) == 5.0
    assert pytest.approx(run_100["recorded"]) == 3.0
    assert run_100["ls_count"] == 2
    assert run_100["has_low_recorded"] is True
    assert pytest.approx(run_101["delivered"]) == 5.0
    assert pytest.approx(run_101["recorded"]) == 12.0
    assert run_101["ls_count"] == 1
    assert run_101["has_low_recorded"] is True
