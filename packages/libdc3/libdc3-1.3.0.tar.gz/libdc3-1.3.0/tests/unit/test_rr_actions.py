from unittest.mock import MagicMock

import pytest

from libdc3.methods.rr_actions import RunRegistryActions


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SSO_CLIENT_ID", "dummy")
    monkeypatch.setenv("SSO_CLIENT_SECRET", "dummy")


@pytest.fixture
def rr_mock(monkeypatch):
    rr = MagicMock()
    monkeypatch.setattr("libdc3.methods.rr_actions.rr", rr)
    return rr


def test_validate_tokens_raises(monkeypatch):
    monkeypatch.delenv("SSO_CLIENT_ID", raising=False)
    monkeypatch.delenv("SSO_CLIENT_SECRET", raising=False)
    with pytest.raises(ValueError):
        RunRegistryActions("A", "B")


def test_init_sets_attrs(rr_mock):
    obj = RunRegistryActions("foo", "bar")
    assert obj.class_name == "foo"
    assert obj.dataset_name == "bar"


def test_fetch_runs_from_all_cycles(rr_mock):
    rr_mock.get_cycles.return_value = [
        {"CycleDataset": [{"run_number": 1}, {"run_number": 2}]},
        {"CycleDataset": [{"run_number": 2}, {"run_number": 3}]},
    ]
    obj = RunRegistryActions("a", "b")
    runs = obj.fetch_runs_from_all_cycles()
    assert runs == [1, 2, 3]


def test_fetch_runs_in_cycles(rr_mock):
    rr_mock.get_cycles.return_value = [
        {"cycle_name": "c1", "CycleDataset": [{"run_number": 1}]},
        {"cycle_name": "c2", "CycleDataset": [{"run_number": 2}]},
    ]
    obj = RunRegistryActions("a", "b")
    runs = obj.fetch_runs_in_cycles(["c2"])
    assert runs == [2]


def test_fetch_open_datasets(rr_mock):
    rr_mock.get_datasets.return_value = [1, 2]
    obj = RunRegistryActions("a", "b")
    result = obj.fetch_open_datasets()
    assert result == [1, 2]
    # With ignore_runs
    obj.fetch_open_datasets(ignore_runs=[123])
    args, kwargs = rr_mock.get_datasets.call_args
    assert "filter" in kwargs or len(args) > 0


def test_fetch_datasets(rr_mock):
    rr_mock.get_datasets.return_value = [1]
    obj = RunRegistryActions("a", "b")
    result = obj.fetch_datasets(min_run=10, max_run=20, ignore_runs=[5])
    assert result == [1]


def test_fetch_runs(rr_mock):
    rr_mock.get_runs.return_value = [{"run_number": 10}, {"run_number": 20}]
    obj = RunRegistryActions("a", "b")
    runs = obj.fetch_runs(run_list=[10, 20])
    assert runs == [10, 20]
    runs = obj.fetch_runs(min_run=5, max_run=25)
    assert runs == [10, 20]
    with pytest.raises(ValueError):
        obj.fetch_runs()


def test_fetch_runs_that_need_update(rr_mock):
    rr_mock.get_runs.return_value = [{"run_number": 1, "state": "OPEN"}, {"run_number": 2, "state": "SIGNOFF"}]
    obj = RunRegistryActions("a", "b")
    result = obj.fetch_runs_that_need_update([1, 2])
    assert {"run_number": 1, "state": "OPEN"} in result


def test_count_offline_rr_lumis(rr_mock):
    rr_mock.get_lumisection_ranges.return_value = [{"end": 42}]
    obj = RunRegistryActions("a", "b")
    assert obj.count_offline_rr_lumis(123) == 42


def test_count_online_rr_lumis(rr_mock):
    rr_mock.get_lumisection_ranges.return_value = [{"end": 99}]
    obj = RunRegistryActions("a", "b")
    assert obj.count_online_rr_lumis(456) == 99


def test_count_oms_lumis(rr_mock):
    rr_mock.get_oms_lumisection_ranges.return_value = [
        {"end": 5, "cms_active": False},
        {"end": 10, "cms_active": True},
        {"end": 15, "cms_active": False},
    ]
    obj = RunRegistryActions("a", "b")
    total, last_active = obj.count_oms_lumis(789)
    assert total == 15
    assert last_active == 10


def test_multi_count_offline_rr_lumis(rr_mock):
    rr_mock.get_lumisection_ranges.side_effect = lambda run, ds: [{"end": run * 2}]
    obj = RunRegistryActions("a", "b")
    result = obj.multi_count_offline_rr_lumis([1, 2])
    assert result == {1: 2, 2: 4}


def test_multi_count_online_rr_lumis(rr_mock):
    rr_mock.get_lumisection_ranges.side_effect = lambda run, ds: [{"end": run + 1}]
    obj = RunRegistryActions("a", "b")
    result = obj.multi_count_online_rr_lumis([3, 4])
    assert result == {3: 4, 4: 5}


def test_multi_count_oms_lumis(rr_mock):
    rr_mock.get_oms_lumisection_ranges.side_effect = lambda run: [{"end": run, "cms_active": True}]
    obj = RunRegistryActions("a", "b")
    result = obj.multi_count_oms_lumis([7, 8])
    assert result[7]["total"] == 7
    assert result[8]["last_cms_active_ls"] == 8


def test_multi_fetch_rr_oms_joint_lumis(rr_mock):
    rr_mock.get_joint_lumisection_ranges.side_effect = lambda run, ds: [
        {"start": 1, "end": 2, "flag": {"status": "GOOD"}}
    ]
    obj = RunRegistryActions("a", "b")
    result = obj.multi_fetch_rr_oms_joint_lumis([1])
    assert result[0]["run_number"] == 1
    assert result[0]["ls_number"] == 1
    assert result[0]["flag"] is True


def test_fetch_rr_oms_joint_lumis(rr_mock):
    rr_mock.get_joint_lumisection_ranges.return_value = [{"start": 1, "end": 2, "flag": {"status": "GOOD"}}]
    obj = RunRegistryActions("a", "b")
    result = obj.fetch_rr_oms_joint_lumis([1])
    assert result[0]["run_number"] == 1
    assert result[0]["ls_number"] == 1
    assert result[0]["flag"] is True


def test_refresh_runs(rr_mock):
    obj = RunRegistryActions("a", "b")
    runobj_list = [{"run_number": 1, "state": "OPEN"}]
    obj.refresh_runs(runobj_list)
    assert rr_mock.move_runs.called
    assert rr_mock.manually_refresh_components_statuses_for_runs.called
    assert rr_mock.move_datasets.called
