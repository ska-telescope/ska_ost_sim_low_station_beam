import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy
import pandas
from astropy.utils.exceptions import AstropyDeprecationWarning
from matplotlib import patches
from matplotlib.ticker import MaxNLocator
from ska_ost_array_config.array_config import (
    LowSubArray,
    get_low_station_coordinates,
    get_low_station_rotation,
)
from ska_sdp_datamodels.configuration.config_coordinate_support import ecef_to_enu

VALID_STATION_NAMES = LowSubArray(subarray_type="AA1").array_config.names.data.tolist()


class LowStation:
    """LowStation class to keep track of full/substations"""

    def __init__(self, station_name, lfaa_list=None):
        """
        Constructor for LowStation class

        Parameters
        ----------
        station_name: string
            Name of a valid SKA LOW station. The current version only supports stations
            available in AA1 configuration.
        lfaa_list: string
            Valid LFAA names (comma-separated) or a selection string.
            If unspecified, all LFAA antennas in the station will be used.
        """
        # Assert that the specified station is supported
        if station_name not in VALID_STATION_NAMES:
            msg = (
                f"Specified station {station_name} is either not supported in this "
                f"version or is an invalid SKA Low station name."
            )
            raise RuntimeError(msg)

        self.station_name = station_name
        self.station_rot_angle = get_low_station_rotation(station_name)

        # Read in the coordinates file for this station
        coord_file_name = (
            Path(__file__).resolve().parent
            / f"lfaa_coords/{station_name}_coordinates.csv"
        )
        self.coordinates = pandas.read_csv(coord_file_name, skiprows=1)
        # Drop unwanted columns
        self.coordinates.drop(["Easting", "Northing", "HAE", "Lat", "Lon", "HAE.1"])
        # Get the ECEF XYZ coordinates of all LFAA
        self.lfaa_names = self.coordinates["#SB-Antenna"].tolist()
        self.lfaa_xyz = numpy.stack(
            (
                self.coordinates["ECEF-X"].to_numpy(),
                self.coordinates["ECEF-Y"].to_numpy(),
                self.coordinates["ECEF-Z"].to_numpy(),
            ),
            axis=1,
        )
        # Convert ECEF coordinates to ENU
        warnings.filterwarnings("ignore", category=AstropyDeprecationWarning)
        self.lfaa_enu = ecef_to_enu(
            get_low_station_coordinates(station_name),
            self.lfaa_xyz,
        )
        warnings.resetwarnings()

    def plot_station_layout(
        self,
        axes=None,
        lfaa_marker_size=10,
        lfaa_marker_color="blue",
        plot_station_boundary=True,
        station_boundary_edge_color="black",
        station_boundary_linewidth=0.5,
        plot_principle_direction=True,
        principle_direction_color="#00bf00",
        principle_direction_alpha=0.5,
        plot_cardinal_direction=True,
        cardinal_direction_alpha=0.5,
        cardinal_direction_color="magenta",
    ):
        """Plot the layout of this station"""
        station_radius = 19.5
        plot_limit = 24.0

        # Create a matplotlib axes if none is provided
        return_vals = False
        if axes is None:
            fig, axes = plt.subplots(1, 1, figsize=(5, 5))
            return_vals = True

        # Plot the LFAA locations
        antenna_marker = mpl.markers.MarkerStyle(marker="+")
        antenna_marker._transform = antenna_marker.get_transform().rotate_deg(
            -self.station_rot_angle
        )
        axes.plot(
            self.lfaa_enu[:, 0],
            self.lfaa_enu[:, 1],
            color=lfaa_marker_color,
            marker=antenna_marker,
            ms=lfaa_marker_size,
            mew=1.0,
            ls="",
        )

        if plot_station_boundary:
            station_boundary = patches.Circle(
                (0.0, 0.0),
                radius=station_radius,
                edgecolor=station_boundary_edge_color,
                facecolor="none",
                linewidth=station_boundary_linewidth,
            )
            axes.add_patch(station_boundary)

        if plot_cardinal_direction:
            axes.plot(
                0,
                station_radius,
                marker="d",
                color=cardinal_direction_color,
                alpha=cardinal_direction_alpha,
                label="Cardinal direction",
            )
            axes.plot(
                [0, 0],
                [0, station_radius],
                color=cardinal_direction_color,
                alpha=cardinal_direction_alpha,
            )

        if plot_principle_direction:
            axes.plot(
                station_radius
                * numpy.cos(numpy.deg2rad(-1 * (self.station_rot_angle - 90))),
                station_radius
                * numpy.sin(numpy.deg2rad(-1 * (self.station_rot_angle - 90))),
                marker="o",
                color=principle_direction_color,
                alpha=principle_direction_alpha,
                label="Principal direction",
            )
            axes.plot(
                [
                    0,
                    station_radius
                    * numpy.cos(numpy.deg2rad(-1 * (self.station_rot_angle - 90))),
                ],
                [
                    0,
                    station_radius
                    * numpy.sin(numpy.deg2rad(-1 * (self.station_rot_angle - 90))),
                ],
                color=principle_direction_color,
                alpha=principle_direction_alpha,
            )

        axes.set_title(
            f"Station {self.station_name} (rotation: {self.station_rot_angle} deg)"
        )
        axes.set_xlabel("X (m)")
        axes.set_ylabel("Y (m)")
        axes.set_xlim(-plot_limit, plot_limit)
        axes.set_ylim(-plot_limit, plot_limit)
        axes.set_aspect("equal")
        axes.set_box_aspect(1)  # Enforce square plots
        axes.grid(color="black", alpha=0.1)
        axes.minorticks_on()
        axes.xaxis.set_major_locator(MaxNLocator(nbins=10))
        axes.yaxis.set_major_locator(MaxNLocator(nbins=10))
        axes.legend(ncol=2)

        if return_vals:
            return fig, axes
