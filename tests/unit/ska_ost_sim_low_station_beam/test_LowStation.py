import pytest
import sunpy

from ska_ost_sim_low_station_beam.LowStation import LowStation


def test_LowStation():
    """Throw NotImplementedError if an invalid station name is specified"""
    with pytest.raises(RuntimeError):
        LowStation("B0")
