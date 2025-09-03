import pytest

from libdc3.methods.lumiloss_analyzer import LumilossAnalyzer


@pytest.fixture
def sample_data():
    rr_oms_lumis = [
        {"run_number": 1, "ls_number": 1, "RR1": True, "OMS1": True},
        {"run_number": 1, "ls_number": 2, "RR1": False, "OMS1": False},
        {"run_number": 2, "ls_number": 1, "RR1": True, "OMS1": True},
    ]
    bril_lumis = [
        {"run_number": 1, "ls_number": 1, "delivered": 10, "recorded": 8, "datetime": "2024-01-01T00:00:00"},
        {"run_number": 1, "ls_number": 2, "delivered": 12, "recorded": 10, "datetime": "2024-01-01T00:01:00"},
        {"run_number": 2, "ls_number": 1, "delivered": 20, "recorded": 18, "datetime": "2024-01-01T00:02:00"},
    ]
    pre_json = {1: [(1, 2)], 2: [(1, 1)]}
    dc_json = {1: [(1, 1)], 2: []}
    low_lumi_runs = []
    ignore_runs = []
    return rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs


def test_parse_and_merge_lumis_basic(sample_data):
    rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs = sample_data
    analyzer = LumilossAnalyzer(rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs, "/ub", "/ub")
    # Only lumisection 1,2 of run 1 and 1,1 of run 2 are in bril_lumis
    # Only run 1, ls 1 is in dc_json, so others should be bad lumis
    bad_lumis = analyzer.bad_lumis
    assert isinstance(bad_lumis, list)
    assert len(bad_lumis) == 2
    assert bad_lumis[0]["run_number"] == 1 and bad_lumis[0]["ls_number"] == 2
    assert bad_lumis[1]["run_number"] == 2 and bad_lumis[1]["ls_number"] == 1


def test_totals_and_efficiencies(sample_data):
    rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs = sample_data
    analyzer = LumilossAnalyzer(rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs, "/ub", "/ub")
    # Only run 1, ls 1 is certified
    results = analyzer.analyze(dcs=["OMS1"], subsystems=["RR1"], subdetectors={"SUBDET": ["RR1"]})
    stats = results["stats"]
    assert stats["total_delivered"] == 10 + 12 + 20
    assert stats["total_recorded"] == 8 + 10 + 18
    assert stats["total_certified"] == 8  # only run 1, ls 1
    assert stats["total_loss"] == 10 + 18  # run 1, ls 2 and run 2, ls 1
    assert stats["data_taking_eff"] == pytest.approx(0.8571428571428571, 0.00001)
    assert stats["recorded_eff"] == pytest.approx(0.2222222222222222, 0.0001)
    assert stats["processed_eff"] == pytest.approx(0.2222222222222222, 0.0001)


def test_low_lumi_and_ignore_runs(sample_data):
    rr_oms_lumis, bril_lumis, pre_json, dc_json, _, _ = sample_data
    # Mark run 2 as low lumi, run 1 as ignore
    analyzer = LumilossAnalyzer(
        rr_oms_lumis,
        bril_lumis,
        pre_json,
        dc_json,
        low_lumi_runs=[2],
        ignore_runs=[1],
        bril_unit="/ub",
        target_unit="/ub",
    )
    assert analyzer.total_low_lumi == 18
    assert analyzer.total_ignore_runs == 8 + 10
    assert analyzer.total_processed == 0
    assert analyzer.total_loss == 0
    assert analyzer.bad_lumis == []


def test_format_lumiloss_by_run(sample_data):
    rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs = sample_data
    analyzer = LumilossAnalyzer(rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs, "/ub", "/ub")
    results = analyzer.analyze(dcs=["OMS1"], subsystems=["RR1"], subdetectors={"SUBDET": ["RR1"]})
    text = analyzer.format_lumiloss_by_run(results["subsystem_run_inclusive_loss"])
    assert "Luminosity unit: /ub" in text
    assert "Subdetector: SUBDET" in text


def test_unit_conversion(sample_data):
    rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs = sample_data
    # bril_unit=ub, target_unit=nb, so multiply by 1e3
    analyzer = LumilossAnalyzer(rr_oms_lumis, bril_lumis, pre_json, dc_json, low_lumi_runs, ignore_runs, "/ub", "/nb")
    assert analyzer.total_delivered == pytest.approx(0.041999999999999996, 0.0001)
    assert analyzer.total_recorded == pytest.approx(0.036000000000000004, 0.0001)
