import pytest

from libdc3.methods.json_producer import JsonProducer


@pytest.fixture
def rr_oms_lumis():
    return [
        {"run_number": 1, "ls_number": 1, "flag1": True, "flag2": True, "prescale_name": None, "prescale_index": None},
        {"run_number": 1, "ls_number": 2, "flag1": True, "flag2": False, "prescale_name": None, "prescale_index": None},
        {
            "run_number": 1,
            "ls_number": 3,
            "flag1": True,
            "flag2": True,
            "prescale_name": "Emergency",
            "prescale_index": 0,
        },
        {"run_number": 2, "ls_number": 1, "flag1": True, "flag2": True, "prescale_name": None, "prescale_index": None},
        {"run_number": 2, "ls_number": 2, "flag1": False, "flag2": True, "prescale_name": None, "prescale_index": None},
    ]


def test_generate_with_oms_flags_only(rr_oms_lumis):
    jp = JsonProducer(rr_oms_lumis)
    result = jp.generate(oms_flags=["flag1", "flag2"])
    # This should not have [3, 3], because prescale_name is set to "Emergency"
    assert result == {1: [[1, 1]], 2: [[1, 1]]}


def test_generate_with_rr_flags(rr_oms_lumis):
    for lumi in rr_oms_lumis:
        lumi["rr_flag"] = True
    jp = JsonProducer(rr_oms_lumis)
    result = jp.generate(oms_flags=["flag1", "flag2"], rr_flags=["rr_flag"])
    # This should have [3, 3], because we are checking the rr_flags - so it ignores the hlt_on_emergency check
    assert result == {1: [[1, 1], [3, 3]], 2: [[1, 1]]}


def test_generate_with_hlt_emergency(rr_oms_lumis):
    jp = JsonProducer(rr_oms_lumis)
    # Should exclude ls_number 3 in run 1 due to Emergency
    result = jp.generate(oms_flags=["flag1", "flag2"])
    assert 3 not in result.get(1, [])


def test_generate_with_ignore_hlt_emergency(rr_oms_lumis):
    jp = JsonProducer(rr_oms_lumis, ignore_hlt_emergency=True)
    result = jp.generate(oms_flags=["flag1", "flag2"])
    # Now Emergency lumisection is included
    assert [3, 3] in result.get(1, [])


def test_generate_empty(
    rr_oms_lumis,
):
    jp = JsonProducer([])
    result = jp.generate(oms_flags=["flag1", "flag2"])
    assert result == {}


def test_group_lumis_by_run_static():
    data = [
        {"run_number": 1, "ls_number": 1},
        {"run_number": 2, "ls_number": 1},
        {"run_number": 1, "ls_number": 2},
    ]
    grouped = JsonProducer._JsonProducer__group_lumis_by_run(data)
    assert set(grouped.keys()) == {1, 2}
    assert len(grouped[1]) == 2
    assert len(grouped[2]) == 1


def test_is_good_lumi_oms_corner_case():
    # Test the special run_number range for beam flags
    jp = JsonProducer([])
    flags = ["beam1_present", "beam2_present", "flag1"]
    lumi_flags = {"beam1_present": False, "beam2_present": False, "flag1": True}
    # Should ignore beam1_present and beam2_present for this run_number
    assert jp._JsonProducer__is_good_lumi_oms(355150, flags, lumi_flags) is True


def test_is_good_lumi_rr_all_flags_true():
    jp = JsonProducer([])
    flags = ["flag1", "flag2"]
    lumi_flags = {"flag1": True, "flag2": True}
    assert jp._JsonProducer__is_good_lumi_rr(flags, lumi_flags) is True


def test_is_good_lumi_rr_some_flags_false():
    jp = JsonProducer([])
    flags = ["flag1", "flag2"]
    lumi_flags = {"flag1": True, "flag2": False}
    assert jp._JsonProducer__is_good_lumi_rr(flags, lumi_flags) is False
