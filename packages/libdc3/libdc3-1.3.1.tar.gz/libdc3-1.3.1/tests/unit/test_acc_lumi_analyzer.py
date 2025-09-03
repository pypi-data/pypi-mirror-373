import random
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from matplotlib.figure import Figure
from PIL import Image

from libdc3.methods.acc_lumi_analyzer import AccLuminosityAnalyzer


@pytest.fixture
def sample_dc_json():
    return {
        1: [(1, 2), (4, 4)],
        2: [(1, 3)],
    }


@pytest.fixture(scope="session")
def sample_bril_lumis():
    start_time = datetime(2024, 4, 6, 0, 24, 10)
    end_time = datetime(2024, 5, 10, 15, 23)
    fill = 9474
    run_number = 378985
    ls_number = 1
    data = []
    while True:
        start_time = start_time + timedelta(seconds=23)
        entry = {
            "time": start_time.strftime("%m/%d/%y %H:%M:%S"),
            "beamstatus": "STABLE BEAMS",
            "E(GeV)": 6800,
            "avgpu": round(random.uniform(24.3, 24.5), 1),
            "source": "HFET",
            "fill": fill,
            "ls_number": ls_number,
            "_ls_number": ls_number,
            "run_number": run_number,
            "datetime": start_time,
            "delivered": round(random.uniform(159.0, 160.8), 9),
            "recorded": round(random.uniform(157.4, 159.0), 9),
        }
        data.append(entry)

        # Generate data to the next lumisection in the next iteration
        ls_number += 1

        # "End the run" if the ls_number is greater then a random number [1, 500]
        if ls_number > random.randint(1, 500):
            run_number += 1
            ls_number = 1

            # Wait some time between runs
            start_time = start_time + timedelta(minutes=random.uniform(1, 30))

            # Increase the fill randomly
            if random.random() > 0.5:
                fill += 1

        if start_time >= end_time:
            break

    return data


@pytest.fixture
def analyzer(sample_dc_json, sample_bril_lumis):
    return AccLuminosityAnalyzer(
        dc_json=sample_dc_json,
        bril_lumis=sample_bril_lumis,
        bril_unit="/ub",
        bril_amodetag="PROTPHYS",
        year=2023,
        plot_energy_label="13 TeV",
        output_path="/tmp",
        target_unit="/fb",
        additional_label_on_plot="Test label",
    )


def test_preprocess_lumis(analyzer):
    lumis = analyzer._AccLuminosityAnalyzer__preprocess_lumis(
        [
            {
                "run_number": 1,
                "ls_number": 1,
                "datetime": datetime(2023, 1, 1, 12, 0),
                "delivered": 10.0,
                "recorded": 8.0,
            },
            {
                "run_number": 1,
                "ls_number": 3,
                "datetime": datetime(2023, 1, 2, 12, 0),
                "delivered": 7.0,
                "recorded": 6.0,
            },
        ]
    )
    assert lumis[0]["is_good"] is True
    assert lumis[1]["is_good"] is False  # ls_number 3 not in good lumisections for run 1


def test_agg_and_cumsum():
    data = [
        {"date": 1, "delivered": 2, "recorded": 1, "is_good": True},
        {"date": 1, "delivered": 3, "recorded": 2, "is_good": False},
        {"date": 2, "delivered": 4, "recorded": 3, "is_good": True},
    ]
    result = AccLuminosityAnalyzer.agg_and_cumsum(data, "date")
    assert result["total_delivered"] == 9
    assert result["total_recorded"] == 6
    assert result["total_certified"] == 4  # Only is_good True


def test_ffill_missing_values():
    data = [
        {"group_key": 1, "delivered_cumsum": 2, "recorded_cumsum": 1, "certified_cumsum": 1},
        {"group_key": 3, "delivered_cumsum": 5, "recorded_cumsum": 3, "certified_cumsum": 2},
    ]
    filled = AccLuminosityAnalyzer.ffill_missing_values(data, 1)
    assert len(filled) == 3
    assert filled[1]["group_key"] == 2
    assert filled[1]["delivered_cumsum"] == 2  # Forward fill


def test_init_sets_fields(analyzer):
    assert analyzer.particle_type == "pp"
    assert analyzer.sqrt_s == "$\\mathbf{\\sqrt{s} =}$"
    assert analyzer.unit_label == "$\\mathbf{fb}^{-1}$"
    assert analyzer.min_datetime < analyzer.max_datetime
    assert isinstance(analyzer.data_by_day, dict)
    assert isinstance(analyzer.data_by_week, dict)


@patch("libdc3.methods.acc_lumi_analyzer.plt")
@patch("libdc3.methods.acc_lumi_analyzer.resources")
@patch("libdc3.methods.acc_lumi_analyzer.Image")
def test_plot_acc_lumi_by_day(mock_image, mock_resources, mock_plt, analyzer):
    mock_image.open.return_value = Image.fromarray(np.zeros((10, 10, 3), dtype=np.uint8))
    mock_resources.files.return_value.__truediv__.return_value = "/tmp/cms_logo.png"
    fig = MagicMock(spec=Figure)
    ax = MagicMock()
    fig.add_subplot.return_value = ax
    mock_plt.figure.return_value = fig
    ax.get_figure.return_value = fig
    fig.get_dpi.return_value = 100
    fig.get_size_inches.return_value = np.array([8, 6])
    ax.get_yticks.return_value = np.array([0, 1, 2])
    ax.get_xticklabels.return_value = []
    ax.get_yticklabels.return_value = []
    ax.legend.return_value.get_texts.return_value = []
    with (
        patch("libdc3.methods.acc_lumi_analyzer.AutoDateLocator"),
        patch("libdc3.methods.acc_lumi_analyzer.DateFormatter"),
    ):
        analyzer.plot_acc_lumi_by_day(save_pdf=True)
    assert mock_plt.close.called


@patch("libdc3.methods.acc_lumi_analyzer.plt")
@patch("libdc3.methods.acc_lumi_analyzer.resources")
@patch("libdc3.methods.acc_lumi_analyzer.Image")
def test_plot_acc_lumi_by_week(mock_image, mock_resources, mock_plt, analyzer):
    mock_image.open.return_value = Image.fromarray(np.zeros((10, 10, 3), dtype=np.uint8))
    mock_resources.files.return_value.__truediv__.return_value = "/tmp/cms_logo.png"
    fig = MagicMock(spec=Figure)
    ax = MagicMock()
    fig.add_subplot.return_value = ax
    mock_plt.figure.return_value = fig
    ax.get_figure.return_value = fig
    fig.get_dpi.return_value = 100
    fig.get_size_inches.return_value = np.array([8, 6])
    ax.get_yticks.return_value = np.array([0, 1, 2])
    ax.get_xticklabels.return_value = []
    ax.get_yticklabels.return_value = []
    ax.legend.return_value.get_texts.return_value = []
    with patch("libdc3.methods.acc_lumi_analyzer.AutoDateLocator"):
        analyzer.plot_acc_lumi_by_week(save_pdf=True)
    assert mock_plt.close.called
