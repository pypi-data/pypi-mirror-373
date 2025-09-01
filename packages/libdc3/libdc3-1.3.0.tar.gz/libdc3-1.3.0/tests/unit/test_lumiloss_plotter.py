from unittest.mock import patch

import pytest

from libdc3.methods.lumiloss_plotter import LumilossPlotter


@pytest.fixture
def sample_lumiloss():
    return {
        "dcs_loss": {"A": 2.0, "B": 0.0, "C": 1.0},
        "subsystems_loss": {"X": 3.0, "Y": 0.0},
        "cms_inclusive_loss": {"CMS1": 5.0, "CMS2": 0.0},
        "cms_exclusive_loss": {"CMS1": 0.002, "CMS2": 0.0005},
        "cms_frac_exclusive_loss": {"CMS1": 0.03, "CMS2": 0.005},
        "cms_detailed_frac_exclusive_loss": {"CMS1": 2.0, "CMS2": 0.5},
        "detector_inclusive_loss": {"CMS1": {"a": 1.0, "b": 0.0}},
        "detector_exclusive_loss": {"CMS2": {"a": 0.5, "b": 0.0}},
    }


@pytest.fixture
def plotter(tmp_path, sample_lumiloss):
    return LumilossPlotter(sample_lumiloss, unit="/ub", output_path=str(tmp_path))


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.LumilossPlotter.bar_plot")
def test_plot_subsystem_dqmflag_loss(mock_bar_plot, mock_makedirs, plotter):
    plotter.plot_subsystem_dqmflag_loss()
    mock_makedirs.assert_called()
    mock_bar_plot.assert_called_once()


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.LumilossPlotter.bar_plot")
def test_plot_dcs_loss(mock_bar_plot, mock_makedirs, plotter):
    plotter.plot_dcs_loss()
    mock_makedirs.assert_called()
    mock_bar_plot.assert_called_once()


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.LumilossPlotter.bar_plot")
def test_plot_cms_inclusive_loss(mock_bar_plot, mock_makedirs, plotter):
    plotter.plot_cms_inclusive_loss()
    mock_makedirs.assert_called()
    mock_bar_plot.assert_called_once()


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.LumilossPlotter.bar_plot")
def test_plot_cms_exclusive_loss(mock_bar_plot, mock_makedirs, plotter):
    plotter.plot_cms_exclusive_loss()
    mock_makedirs.assert_called()
    mock_bar_plot.assert_called_once()


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.LumilossPlotter.bar_plot")
def test_plot_cms_detailed_fraction_exclusive_loss(mock_bar_plot, mock_makedirs, plotter):
    plotter.plot_cms_detailed_fraction_exclusive_loss()
    mock_makedirs.assert_called()
    mock_bar_plot.assert_called_once()


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.LumilossPlotter.bar_plot")
def test_plot_inclusive_loss_by_subdetector(mock_bar_plot, mock_makedirs, plotter):
    plotter.plot_inclusive_loss_by_subdetector()
    mock_makedirs.assert_called()
    mock_bar_plot.assert_called_once()


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.LumilossPlotter.bar_plot")
def test_plot_exclusive_loss_by_subdetector(mock_bar_plot, mock_makedirs, plotter):
    plotter.plot_exclusive_loss_by_subdetector()
    mock_makedirs.assert_called()
    mock_bar_plot.assert_called_once()


@patch("libdc3.methods.lumiloss_plotter.os.makedirs")
@patch("libdc3.methods.lumiloss_plotter.plt")
def test_plot_fraction_of_exclusive_loss_by_subdetector(mock_plt, mock_makedirs, plotter):
    plotter.plot_fraction_of_exclusive_loss_by_subdetector()
    mock_makedirs.assert_called()
    assert mock_plt.pie.called
    assert mock_plt.savefig.called
    assert mock_plt.close.called


def test_gt_thr():
    d = {"a": 1, "b": 0, "c": -1}
    assert LumilossPlotter.gt_thr(d, 0) == {"a": 1}


def test_gte_thr():
    d = {"a": 1, "b": 0, "c": -1}
    assert LumilossPlotter.gte_thr(d, 0) == {"a": 1, "b": 0}


def test_sort_by_values():
    d = {"a": 2, "b": 1, "c": 3}
    sorted_d = LumilossPlotter.sort_by_values(d)
    assert list(sorted_d.keys()) == ["b", "a", "c"]
