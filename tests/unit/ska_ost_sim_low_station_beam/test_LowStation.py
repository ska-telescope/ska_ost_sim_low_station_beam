from pathlib import Path

import pytest
from astropy import units
from astropy.coordinates import EarthLocation
from matplotlib.testing.compare import compare_images

from ska_ost_sim_low_station_beam.LowStation import LowStation

TOLERANCE = 1e-3


def test_LowStation():
    """Throw NotImplementedError if an invalid station name is specified"""
    with pytest.raises(RuntimeError):
        LowStation("B0")


def test_get_lfaa_coordinates():
    """Test LowStation.get_lfaa_coordinates()"""
    expected_answer = EarthLocation.from_geocentric(
        -2561216.6924, 5085891.1196, -2864164.6997, unit=units.m
    )
    test = LowStation("S8-1").get_lfaa_coordinates("SB01-01")
    assert expected_answer == test


def test_get_lfaa_coordinates_fail():
    """
    LowStation.get_lfaa_coordinates() must throw a RuntimeError if an invalid LFAA
    is specified.
    """
    # Throw RuntimeError if an invalid station name is specified
    with pytest.raises(RuntimeError):
        LowStation("S8-1").get_lfaa_coordinates("SB01-01,SB00-01")


def test_plot_station_layout(test_image_name):
    """Test LowStation.plot_station_layout() function"""
    station = LowStation("S8-1")

    # Test without legend
    fig, axes = station.plot_station_layout()
    fig.savefig(test_image_name)
    reference_image = (
        Path(__file__).resolve().parent.parent / "static/low_S8_1_station_layout.png"
    )
    assert compare_images(test_image_name, reference_image, tol=TOLERANCE) is None

    # Test with legend
    fig, axes = station.plot_station_layout(
        plot_station_boundary=True,
        plot_principle_direction=True,
        plot_cardinal_direction=True,
    )
    fig.savefig(test_image_name)
    reference_image = (
        Path(__file__).resolve().parent.parent
        / "static/low_S8_1_station_layout_with_legend.png"
    )
    assert compare_images(test_image_name, reference_image, tol=TOLERANCE) is None
