import fnmatch
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy
import pandas
from astropy import units
from astropy.coordinates import EarthLocation
from astropy.utils.exceptions import AstropyDeprecationWarning
from matplotlib import patches
from matplotlib.ticker import MaxNLocator
from ska_ost_array_config.array_config import (
    LowSubArray,
    get_low_station_coordinates,
    get_low_station_rotation,
)
from ska_sdp_datamodels.configuration.config_coordinate_support import ecef_to_enu

VALID_STATION_TYPES = LowSubArray(
    subarray_type="AA1"
).array_config.names.data.tolist() + ["substation"]


class LowStation:
    """LowStation class to keep track of full/substations"""

    def __init__(
        self, station_type, station_name=None, parent_station=None, lfaa_list=None
    ):
        """
        Constructor for LowStation class

        Parameters
        ----------
        station_type: string
            Name of a valid SKA LOW station. The current version only supports stations
            available in AA1 configuration.
        lfaa_list: string
            Valid LFAA names (comma-separated) or a selection string.
            If unspecified, all LFAA antennas in the station will be used.
        """
        # Assert that the specified station is supported
        if station_type not in VALID_STATION_TYPES:
            msg = f"Station type {station_type} is invalid. "
            msg += f"Valid station types are {', '.join(VALID_STATION_TYPES)}"
            raise ValueError(msg)

        if station_type == "substation":
            # Substation is being defined
            self.station_type = station_type
            self.station_name = station_name
            self.parent_station = parent_station
            self.station_rot_angle = get_low_station_rotation(self.parent_station)
            # Read in the coordinates file for this station
            coord_file_name = (
                Path(__file__).resolve().parent
                / f"lfaa_coords/{self.parent_station}_coordinates.csv"
            )
            all_coordinates = pandas.read_csv(coord_file_name, skiprows=1)
            all_lfaa = all_coordinates["#SB-Antenna"].tolist()
            if lfaa_list is None:
                requested_lfaa = all_lfaa
            else:
                requested_lfaa = []
                for pattern in lfaa_list.split(","):
                    matched_lfaa = fnmatch.filter(all_lfaa, pattern)
                    if not matched_lfaa:
                        # The selection pattern did not resolve into valid LFAA names
                        msg = f"{pattern} is not a valid selection string. "
                        msg += "Check your inputs."
                        raise ValueError(msg)
                    else:
                        requested_lfaa += matched_lfaa
            requested_lfaa = sorted(list(set(requested_lfaa)))
            # Retain only those LFAAs requested in this substation
            self.coordinates = all_coordinates[
                all_coordinates["#SB-Antenna"].isin(requested_lfaa)
            ]
        else:
            # Full station is being defined
            self.station_type = station_type
            self.station_name = station_type
            self.parent_station = station_type
            self.station_rot_angle = get_low_station_rotation(station_type)
            # Read in the coordinates file for this station
            coord_file_name = (
                Path(__file__).resolve().parent
                / f"lfaa_coords/{self.parent_station}_coordinates.csv"
            )
            self.coordinates = pandas.read_csv(coord_file_name, skiprows=1)

        # Drop unwanted columns
        self.coordinates = self.coordinates.drop(
            ["Easting", "Northing", "HAE", "Lat", "Lon", "HAE.1"], axis=1
        )
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
            get_low_station_coordinates(self.parent_station),
            self.lfaa_xyz,
        )
        warnings.resetwarnings()

    def filter_lfaa_by_distance(self, distance, invert=False):
        """
        Generates a list of LFAA that lie within the specified distance from the
        array_centre.

        Parameters
        ----------
        distance: float or astropy.units.quantity.Quantity equivalent to astropy.units.m
            Distance in metres (for float) from the center of the station within which
            the filtered LFAA elements must lie.
        invert: bool
            If invert=True, LFAA elements outside the specified distance is returned.
            Default: False

        Returns
        -------
        Comma-separated list of LFAA elements
        """
        if isinstance(distance, units.quantity.Quantity):
            if not distance.unit.is_equivalent(units.m):
                raise ValueError(
                    f"Input unit of distance is not equivalent to m: {distance}"
                )
            else:
                distance = distance.to(units.m).value

        distance_from_centre = numpy.sqrt(
            self.lfaa_enu[:, 0] ** 2 + self.lfaa_enu[:, 1] ** 2
        )

        if invert:
            return ",".join(
                numpy.asarray(self.lfaa_names)[distance_from_centre > distance].tolist()
            )
        else:
            return ",".join(
                numpy.asarray(self.lfaa_names)[distance_from_centre < distance].tolist()
            )

    def get_neighbour_lfaa(self, ref_lfaa, distance):
        """
        Generates a list of LFAA that lie within the specified distance from ref_lfaa.

        Parameters
        ----------
        ref_lfaa: string
            Name of a valid LFAA element in this station
        distance: float or astropy.units.quantity.Quantity equivalent to astropy.units.m
            Distance in metres (for float) from the center of the station within which
            the filtered LFAA elements must lie.
        """
        if isinstance(distance, units.quantity.Quantity):
            if not distance.unit.is_equivalent(units.m):
                raise ValueError(
                    f"Input unit of distance is not equivalent to m: {distance}"
                )
            else:
                distance = distance.to(units.m).value
        try:
            index = self.lfaa_names.index(ref_lfaa)
        except ValueError:
            msg = f"LFAA {ref_lfaa} is not present in this station"
            raise ValueError(msg)
        ref_coords = self.lfaa_enu[index]
        distance_from_ref = numpy.sqrt(
            (self.lfaa_enu[:, 0] - ref_coords[0]) ** 2
            + (self.lfaa_enu[:, 1] - ref_coords[1]) ** 2
        )
        return ",".join(
            numpy.asarray(self.lfaa_names)[distance_from_ref < distance].tolist()
        )

    def get_lfaa_names(self):
        """Returns as a list the names of the LFAA included in this LowStation"""
        return self.lfaa_names

    def get_lfaa_coordinates(self, lfaa_names):
        """
        Returns the coordinates of the specified LFAAs

        Parameters
        ----------
        lfaa_names: string
            Comma-separated list of LFAA names

        Returns
        -------
        List of astropy.coordinates.EarthLocation objects with the same length
        as lfaa_names.
        """
        coordinates = []
        for lfaa_name in lfaa_names.split(","):
            mask = self.coordinates["#SB-Antenna"].str.fullmatch(lfaa_name)
            if not mask.any():
                msg = f"{lfaa_name} is not a valid LFAA in station {self.station_name}"
                raise ValueError(msg)
            coordinates.append(
                EarthLocation.from_geocentric(
                    self.coordinates["ECEF-X"][mask],
                    self.coordinates["ECEF-Y"][mask],
                    self.coordinates["ECEF-Z"][mask],
                    unit=units.m,
                )
            )
        return coordinates

    def plot_station_layout(
        self,
        axes=None,
        lfaa_marker_size=10,
        lfaa_marker_color="blue",
        plot_station_boundary=False,
        station_boundary_edge_color="black",
        station_boundary_linewidth=0.5,
        station_boundary_alpha=0.5,
        plot_principle_direction=False,
        principle_direction_color="#00bf00",
        principle_direction_alpha=0.5,
        plot_cardinal_direction=False,
        cardinal_direction_alpha=0.5,
        cardinal_direction_color="magenta",
    ):
        """
        Plot the layout of this station

        Parameters
        ----------
        axes:
        lfaa_marker_size: float
            Size of the symbol used to plot the antenna. Default: 10.
        lfaa_marker_color: string
            Colour of the LFAA marker. Can be a valid matplotlib-compatible colour
            name or hex string. Default: 'blue'
        plot_station_boundary: bool
            If True, plot the station boundary. Default: False
        station_boundary_edge_color: string
            Colour of the station boundary. Can be a valid matplotlib-compatible colour
            name or hex string. Default: 'black'
        station_boundary_linewidth: float
            Line width of the station boundary. Default: 0.5
        station_boundary_alpha: float
            Default: 0.5
        plot_principle_direction: bool
            If True, plot a line indicating the station principle direction.
            Default: False
        principle_direction_color: string
            Colour of the station principle direction marker.
            Can be a valid matplotlib-compatible colour name or hex string.
            Default: "#00bf00"
        principle_direction_alpha: float
            Default: 0.5
        plot_cardinal_direction: bool
            If True, plot a line indicating the station principle direction.
            Default: False
        cardinal_direction_color: string
            Colour of the cardinal direction marker.
            Can be a valid matplotlib-compatible colour name or hex string.
            Default: "magenta"
        cardinal_direction_alpha: float
            Default: 0.5
        """
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

        show_legend = False

        if plot_station_boundary:
            station_boundary = patches.Circle(
                (0.0, 0.0),
                radius=station_radius,
                edgecolor=station_boundary_edge_color,
                facecolor="none",
                linewidth=station_boundary_linewidth,
                alpha=station_boundary_alpha,
            )
            axes.add_patch(station_boundary)

        if plot_cardinal_direction:
            show_legend = True
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
            show_legend = True
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
        if show_legend:
            axes.legend(ncol=2)

        if return_vals:
            return fig, axes
