from unittest import mock

import pytest

from libdc3.methods.era_plotter import EraPlotter


@pytest.fixture
def sample_eras_statistics():
    return [
        {
            "era": "A",
            "start_run": 1,
            "end_run": 10,
            "lhc_delivered": 100.0,
            "cms_recorded": 80.0,
            "total_low_lumi": 5.0,
            "total_ignore_runs": 2.0,
            "total_not_stable_beams": 1.0,
            "total_not_in_oms_rr": 0.5,
            "dc_processed": 70.0,
            "total_loss": 10.0,
            "dc_certified": 60.0,
            "processed_eff": 60.0 / 70.0,
            "data_taking_eff": 80.0 / 100.0,
            "recorded_eff": 60.0 / 80.0,
        },
        {
            "era": "B",
            "start_run": 11,
            "end_run": 20,
            "lhc_delivered": 200.0,
            "cms_recorded": 150.0,
            "total_low_lumi": 10.0,
            "total_ignore_runs": 3.0,
            "total_not_stable_beams": 2.0,
            "total_not_in_oms_rr": 1.0,
            "dc_processed": 120.0,
            "total_loss": 20.0,
            "dc_certified": 100.0,
            "processed_eff": 100.0 / 120.0,
            "data_taking_eff": 150.0 / 200.0,
            "recorded_eff": 100.0 / 150.0,
        },
    ]


@pytest.fixture
def output_path(tmp_path):
    return str(tmp_path)


def test_add_all_in_appends_summary(sample_eras_statistics, output_path):
    eras = [dict(e) for e in sample_eras_statistics]  # deep copy
    plotter = EraPlotter(eras, 2020, output_path)
    assert len(plotter.eras_statistics) == 3
    all_in = plotter.eras_statistics[-1]
    assert all_in["era"] == "ALL IN"
    assert all_in["start_run"] == 1
    assert all_in["end_run"] == 20
    assert pytest.approx(all_in["lhc_delivered"]) == 300.0
    assert pytest.approx(all_in["cms_recorded"]) == 230.0
    assert pytest.approx(all_in["dc_processed"]) == 190.0
    assert pytest.approx(all_in["dc_certified"]) == 160.0
    assert pytest.approx(all_in["processed_eff"]) == 160.0 / 190.0
    assert pytest.approx(all_in["data_taking_eff"]) == 230.0 / 300.0
    assert pytest.approx(all_in["recorded_eff"]) == 160.0 / 230.0


@mock.patch("libdc3.methods.era_plotter.plt")
def test_plot_dc_efficiency_by_processed_per_era_creates_files(mock_plt, sample_eras_statistics, output_path):
    # Mock plt.subplots to return mock fig, ax
    mock_fig = mock.Mock()
    mock_ax = mock.Mock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)
    plotter = EraPlotter([dict(e) for e in sample_eras_statistics], 2020, output_path)
    plotter.plot_dc_efficiency_by_processed_per_era(save_pdf=True)
    # Check bar called for each era
    assert mock_ax.bar.call_count == 3
    # Check savefig called for png and pdf
    assert mock_fig.savefig.call_count == 2
    args_png, kwargs_png = mock_fig.savefig.call_args_list[0]
    args_pdf, kwargs_pdf = mock_fig.savefig.call_args_list[1]
    assert args_png[0].endswith("dc_efficiency_by_processed_per_era.png")
    assert args_pdf[0].endswith("dc_efficiency_by_processed_per_era.pdf")
    # Check plt.close called
    assert mock_plt.close.called


@mock.patch("libdc3.methods.era_plotter.plt")
def test_plot_dc_efficiency_by_recorded_per_era_creates_files(mock_plt, sample_eras_statistics, output_path):
    mock_fig = mock.Mock()
    mock_ax = mock.Mock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)
    plotter = EraPlotter([dict(e) for e in sample_eras_statistics], 2020, output_path)
    plotter.plot_dc_efficiency_by_recorded_per_era(save_pdf=False)
    # Check bar called for each era
    assert mock_ax.bar.call_count == 3
    # Only png should be saved
    assert mock_fig.savefig.call_count == 1
    args_png, kwargs_png = mock_fig.savefig.call_args
    assert args_png[0].endswith("dc_efficiency_by_recorded_per_era.png")
    assert mock_plt.close.called


def test_plotter_handles_empty_eras(output_path):
    with pytest.raises(ZeroDivisionError):
        EraPlotter([], 2020, output_path)
