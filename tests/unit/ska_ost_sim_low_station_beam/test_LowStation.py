from pathlib import Path

import pytest
from astropy import units
from astropy.coordinates import EarthLocation
from matplotlib.testing.compare import compare_images
from ska_ost_array_config.array_config import LowSubArray

from ska_ost_sim_low_station_beam.LowStation import LowStation

TOLERANCE = 1e-3


def test_LowStation():
    """Test LowStation class"""
    with pytest.raises(ValueError):
        LowStation("B0")


def test_all_valid_AA1_stations():
    """Check that all valid AA1 stations can be specified"""
    for name in LowSubArray(subarray_type="AA1").array_config.names.data.tolist():
        assert isinstance(LowStation(name), LowStation)


def test_get_lfaa_coordinates():
    """Test LowStation.get_lfaa_coordinates()"""
    expected_answer = EarthLocation.from_geocentric(
        -2561216.8527, 5085891.0873, -2864164.4719, unit=units.m
    )
    test = LowStation("S8-1").get_lfaa_coordinates("SB01-01")
    assert expected_answer == test


def test_get_lfaa_coordinates_fail():
    """
    LowStation.get_lfaa_coordinates() must throw a ValueError if an invalid LFAA
    is specified.
    """
    # Throw ValueError if an invalid station name is specified
    with pytest.raises(ValueError):
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


def test_LowStation_substation_fail():
    """Test if LowStation throws a ValueError if an invalid LFAA name is specified"""
    with pytest.raises(ValueError):
        LowStation(
            station_type="substation",
            station_name="sub_s8_1",
            parent_station="S8-1",
            lfaa_list="SB01-01,SB01-02,SB01-00",
        )


def test_LowStation_get_neighbour_lfaa():
    """Test LowStation.get_neighbour_lfaa"""
    # Invalid ref_lfaa should throw a ValueError
    with pytest.raises(ValueError):
        LowStation("S8-1").get_neighbour_lfaa("SB05-00", distance=10.0)

    assert LowStation("S8-1").get_neighbour_lfaa("SB05-09", distance=1.0) == "SB05-09"


def test_LowStation_filter_lfaa_by_distance():
    """Test LowStation.filter_lfaa_by_distance"""
    with pytest.raises(ValueError):
        LowStation("S8-1").filter_lfaa_by_distance(distance=10.0 * units.second)
