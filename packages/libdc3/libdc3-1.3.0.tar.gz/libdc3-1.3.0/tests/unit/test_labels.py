import pytest

from libdc3.labels import LATEX_UNITS, PARTICLE_TYPES, SQRT_S


def test_latex_units_content():
    assert "/fb" in LATEX_UNITS
    assert LATEX_UNITS["/fb"] == "$\\mathbf{fb}^{-1}$"
    assert "Hz/ub" in LATEX_UNITS
    assert LATEX_UNITS["Hz/ub"] == "$\\mathbf{Hz/}\\mathbf{\\mu}\\mathbf{b}$"
    with pytest.raises(KeyError):
        _ = LATEX_UNITS["/zb"]


def test_particle_types_content():
    assert "PROTPHYS" in PARTICLE_TYPES
    assert PARTICLE_TYPES["PROTPHYS"] == "pp"
    assert "IONPHYS" in PARTICLE_TYPES
    assert PARTICLE_TYPES["IONPHYS"] == "PbPb"
    with pytest.raises(KeyError):
        _ = PARTICLE_TYPES["UNKNOWN"]


def test_sqrt_s_content():
    assert "IONPHYS" in SQRT_S
    assert SQRT_S["IONPHYS"] == "$\\mathbf{\\sqrt{s_{NN}} =}$"
    assert "PROTPHYS" in SQRT_S
    assert SQRT_S["PROTPHYS"] == "$\\mathbf{\\sqrt{s} =}$"
    with pytest.raises(KeyError):
        _ = SQRT_S["NOTYPE"]
