from unittest.mock import MagicMock, patch

import pytest

from libdc3.methods.next_call import NextCallError, NextCallGenerator


@pytest.fixture
def mock_rr_actions():
    mock = MagicMock()
    mock.fetch_runs_from_all_cycles.return_value = [1]
    mock.fetch_open_datasets.return_value = [{"run_number": 2}, {"run_number": 3}]
    mock.fetch_runs_that_need_update.return_value = [2]
    mock.refresh_runs.return_value = None
    mock.multi_count_online_rr_lumis.return_value = {2: 10, 3: 12}
    mock.multi_count_offline_rr_lumis.return_value = {2: 10, 3: 12}
    mock.multi_count_oms_lumis.return_value = {
        2: {"total": 10, "last_cms_active_ls": 10},
        3: {"total": 12, "last_cms_active_ls": 12},
    }
    return mock


@pytest.fixture
def mock_bril_actions():
    mock = MagicMock()
    mock.fetch_lumis.return_value = {
        "detailed": [
            {"run_number": 2, "ls_number": 1, "delivered": 1.0, "recorded": 1.0, "datetime": "2024-01-01T00:00:00"},
            {"run_number": 3, "ls_number": 1, "delivered": 1.0, "recorded": 1.0, "datetime": "2024-01-01T00:00:00"},
        ]
    }
    mock.agg_by_run.return_value = [
        {"run_number": 2, "ls_count": 10, "has_low_recorded": False},
        {"run_number": 3, "ls_count": 12, "has_low_recorded": False},
    ]
    return mock


@pytest.fixture
def mock_caf():
    mock = MagicMock()
    mock.download.return_value = {"2": {}, "3": {}}
    mock.latest = {"name": "dcs.json"}
    return mock


@pytest.fixture
def mock_dqmgui():
    mock = MagicMock()
    mock.check_if_runs_are_present.side_effect = lambda dt, runs: []
    return mock


@pytest.fixture
def mock_dc3_config():
    mock = MagicMock()
    mock.AUTH_CERT = "cert"
    mock.AUTH_CERT_KEY = "key"
    mock.validate_x509cert.return_value = None
    return mock


@pytest.fixture
def generator(monkeypatch, mock_rr_actions, mock_bril_actions, mock_caf, mock_dqmgui, mock_dc3_config):
    with (
        patch("libdc3.methods.next_call.RunRegistryActions", return_value=mock_rr_actions),
        patch("libdc3.methods.next_call.BrilActions", return_value=mock_bril_actions),
        patch("libdc3.methods.next_call.CAF", return_value=mock_caf),
        patch("libdc3.methods.next_call.DQMGUI", return_value=mock_dqmgui),
        patch("libdc3.methods.next_call.dc3_config", mock_dc3_config),
    ):
        yield NextCallGenerator(
            rr_class_name="class",
            rr_dataset_name="dataset",
            bril_brilws_version="v1",
            bril_unit="unit",
            bril_low_lumi_thr=1.0,
            gui_lookup_datasets=["datasetA", "datasetB"],
        )


def test_get_initial_run_list(generator, mock_rr_actions):
    runs = generator.get_initial_run_list()
    assert runs == [2, 3]
    mock_rr_actions.fetch_runs_from_all_cycles.assert_called_once()
    mock_rr_actions.fetch_open_datasets.assert_called_once_with([1])


def test_check_and_fix_online_rr_oms_mismatches_no_refresh(generator, mock_rr_actions):
    mismatches = generator.check_and_fix_online_rr_oms_mismatches([2, 3])
    assert mismatches == [2]
    mock_rr_actions.fetch_runs_that_need_update.assert_called_once_with([2, 3])
    mock_rr_actions.refresh_runs.assert_not_called()


def test_check_and_fix_online_rr_oms_mismatches_with_refresh(monkeypatch, mock_rr_actions, generator):
    generator.refresh_runs_if_needed = True
    mismatches = generator.check_and_fix_online_rr_oms_mismatches([2, 3])
    assert mismatches == [2]
    mock_rr_actions.refresh_runs.assert_called_once_with([2])


def test_get_bril_lumis_by_run(generator, mock_bril_actions):
    result = generator.get_bril_lumis_by_run([2, 3])
    assert result == [
        {"run_number": 2, "ls_count": 10, "has_low_recorded": False},
        {"run_number": 3, "ls_count": 12, "has_low_recorded": False},
    ]
    mock_bril_actions.fetch_lumis.assert_called_once()
    mock_bril_actions.agg_by_run.assert_called_once()


def test_check_rr_oms_bril_mismatches(generator):
    run_list = [2, 3]
    bril_by_run = [
        {"run_number": 2, "ls_count": 10, "has_low_recorded": False},
        {"run_number": 3, "ls_count": 12, "has_low_recorded": False},
    ]
    forced, loose = generator.check_rr_oms_bril_mismatches(run_list, bril_by_run)
    assert forced == []
    assert loose == []


def test_check_runs_not_in_bril(generator):
    run_list = [2, 3, 4]
    bril_by_run = [
        {"run_number": 2, "ls_count": 10, "has_low_recorded": False},
        {"run_number": 3, "ls_count": 12, "has_low_recorded": False},
    ]
    not_in_bril = generator.check_runs_not_in_bril(run_list, bril_by_run)
    assert not_in_bril == [4]


def test_check_low_lumi_runs(generator):
    bril_by_run = [
        {"run_number": 2, "ls_count": 10, "has_low_recorded": False},
        {"run_number": 3, "ls_count": 12, "has_low_recorded": True},
    ]
    low_lumi = generator.check_low_lumi_runs(bril_by_run)
    assert low_lumi == [{"run_number": 3, "ls_count": 12, "has_low_recorded": True}]


def test_check_dcs_json(generator, mock_caf):
    run_list = [2, 3, 4]
    result = generator.check_dcs_json(run_list)
    assert result["filename"] == "dcs.json"
    assert result["run_numbers"] == [4]


def test_check_runs_not_in_dqmgui(generator, mock_dqmgui):
    run_list = [2, 3]
    result = generator.check_runs_not_in_dqmgui(run_list)
    assert result == {"datasetA": [], "datasetB": []}
    assert mock_dqmgui.check_if_runs_are_present.call_count == 2


def test_generate_success(generator):
    result = generator.generate()
    assert set(result.keys()) == {
        "initial_run_list",
        "online_rr_oms_mismatches",
        "runs_not_in_bril",
        "rr_oms_bril_mismatches_forced_inequality",
        "rr_oms_bril_mismatches_loose",
        "low_lumi_runs",
        "not_in_dcs_runs",
        "not_in_dqmgui_datasets",
        "final_run_list",
    }
    assert result["final_run_list"] == [2, 3]


def test_generate_empty_initial(monkeypatch, generator):
    monkeypatch.setattr(generator, "get_initial_run_list", lambda: [])
    with pytest.raises(NextCallError):
        generator.generate()
