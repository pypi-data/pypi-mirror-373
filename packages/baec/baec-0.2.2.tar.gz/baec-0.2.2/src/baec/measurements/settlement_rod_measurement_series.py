from __future__ import annotations

from functools import cache
from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import SettlementRodMeasurement
from baec.project import Project


class SettlementRodMeasurementSeries:
    """
    Represents a series of measurements for a single settlement rod.
    """

    def __init__(self, measurements: List[SettlementRodMeasurement]) -> None:
        """
        Initializes a SettlementRodMeasurementSeries object.

        Parameters
        ----------
        measurements : List[SettlementRodMeasurement]
            The list of measurements for the settlement rod.

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, device, object or
            coordinate refence systems.
        """

        # Initialize all attributes using private setters.
        self._set_measurements(measurements)

    def _set_measurements(self, value: List[SettlementRodMeasurement]) -> None:
        """Private setter for measurements attribute."""

        # Check if the input is a list of SettlementRodMeasurement objects.
        if not all(isinstance(item, SettlementRodMeasurement) for item in value):
            raise TypeError(
                "Expected 'List[SettlementRodMeasurement]' type for 'measurements' attribute."
            )

        # Check if the list is not empty.
        if not value:
            raise ValueError("Empty list not allowed for 'measurements' attribute.")

        # Check that the measurements are for the same project.
        projects = []
        for measurement in value:
            if measurement.project not in projects:
                projects.append(measurement.project)
        if len(projects) > 1:
            raise ValueError(
                "All measurements must be for the same project. "
                + f"The following projects are found: {projects}"
            )

        # Check that the measurements are for the same device.
        measurement_devices = []
        for measurement in value:
            if measurement.device not in measurement_devices:
                measurement_devices.append(measurement.device)
        if len(measurement_devices) > 1:
            raise ValueError(
                "All measurements must be for the same device. "
                + f"The following devices are found: {measurement_devices}"
            )

        # Check that the measurements are for the same object.
        object_ids = []
        for measurement in value:
            if measurement.object_id not in object_ids:
                object_ids.append(measurement.object_id)
        if len(object_ids) > 1:
            raise ValueError(
                "All measurements must be for the same measured object. "
                + f"The following object IDs are found: {object_ids}"
            )

        # Check that the measurements are all in the same coordinate reference systems.
        crs_list = []
        for measurement in value:
            if measurement.coordinate_reference_systems not in crs_list:
                crs_list.append(measurement.coordinate_reference_systems)
        if len(crs_list) > 1:
            raise ValueError(
                "All measurements must be in the same coordinate reference systems. "
                + f"The following object IDs are found: {crs_list}"
            )

        # Organize the list of measurements in chronological order.
        self._measurements = sorted(value, key=lambda x: x.date_time)

    @property
    def measurements(self) -> List[SettlementRodMeasurement]:
        """
        The list of measurements for the settlement rod.
        They are organized in chronological order.
        """
        return self._measurements

    @property
    def project(self) -> Project:
        """
        The project which all the measurements belongs to.
        """
        return self._measurements[0].project

    @property
    def device(self) -> MeasurementDevice:
        """
        The measurement device.
        """
        return self._measurements[0].device

    @property
    def object_id(self) -> str:
        """
        The ID of the measured object.
        """
        return self._measurements[0].object_id

    @property
    def coordinate_reference_systems(self) -> CoordinateReferenceSystems:
        """
        The horizontal (X, Y) and vertical (Z) coordinate reference systems of the measurements.
        """
        return self._measurements[0].coordinate_reference_systems

    @cache
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the series of measurements to a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with the measurements. The columns of the DataFrame are:
            project_id, project_name, device_id, device_qr_code, object_id,
            coordinate_horizontal_epsg_code, coordinate_vertical_epsg_code,
            date_time, rod_top_x, rod_top_y, rod_top_z, rod_length, rod_bottom_z
            rod_bottom_z_uncorrected, ground_surface_z, status, status_messages, temperature,
            voltage.
        """
        return pd.DataFrame.from_records(
            [measurement.to_dict() for measurement in self.measurements]
        )

    def plot_x_time(self, axes: Axes | None = None) -> Axes:
        """
        Plot the horizontal X-coordinates at the top of the rod over time.

        Parameters
        ----------
        axes: plt.Axes
            Axes to create the figure

        Returns
        -------
        plt.Axes
        """
        if axes is not None:
            if not isinstance(axes, Axes):
                raise TypeError("Expected 'Axes' type or None for 'axes' parameter.")

        if axes is None:
            axes = plt.gca()

        df = self.to_dataframe()

        df.plot(
            x="date_time",
            y="rod_top_x",
            ax=axes,
            legend=True,
        )

        axes.set_ylim(df["rod_top_x"].min() - 0.5, df["rod_top_x"].max() + 0.5)
        axes.grid()

        axes.set_ylabel(f"X [{self.coordinate_reference_systems.horizontal_units}]")
        axes.set_xlabel("Date and Time")
        axes.set_title(f"Horizontal X measurements for object: {self.object_id}")

        return axes

    def plot_y_time(self, axes: Axes | None = None) -> Axes:
        """
        Plot the horizontal Y-coordinates at the top of the rod over time.

        Parameters
        ----------
        axes: plt.Axes
            Axes to create the figure

        Returns
        -------
        plt.Axes
        """
        if axes is not None:
            if not isinstance(axes, Axes):
                raise TypeError("Expected 'Axes' type or None for 'axes' parameter.")

        if axes is None:
            axes = plt.gca()

        df = self.to_dataframe()

        df.plot(
            x="date_time",
            y="rod_top_y",
            ax=axes,
            legend=True,
        )

        axes.set_ylim(df["rod_top_y"].min() - 0.5, df["rod_top_y"].max() + 0.5)
        axes.grid()

        axes.set_ylabel(f"Y [{self.coordinate_reference_systems.horizontal_units}]")
        axes.set_xlabel("Date and Time")
        axes.set_title(f"Horizontal Y measurements for object: {self.object_id}")

        return axes

    def plot_z_time(self, axes: Axes | None = None) -> Axes:
        """
        Plot the vertical Z-coordinates at the top the rod, the ground surface and the bottom of the
        rod over time.

        Parameters
        ----------
        axes: plt.Axes
            Axes to create the figure

        Returns
        -------
        plt.Axes
        """
        if axes is not None:
            if not isinstance(axes, Axes):
                raise TypeError("Expected 'Axes' type or None for 'axes' parameter.")

        if axes is None:
            axes = plt.gca()

        df = self.to_dataframe()
        z_cols = ["rod_top_z", "ground_surface_z", "rod_bottom_z"]

        df.plot(
            x="date_time",
            y=z_cols,
            ax=axes,
            legend=True,
        )

        axes.set_ylim(
            np.nanmin(df[z_cols].values) - 0.5, np.nanmax(df[z_cols].values) + 0.5
        )
        axes.grid()

        axes.set_ylabel(self.coordinate_reference_systems.vertical_datum_and_units)
        axes.set_xlabel("Date and Time")
        axes.set_title(f"Vertical Z measurements for object: {self.object_id}")

        return axes

    def plot_xyz_time(self) -> Figure:
        """
        Plot in a new figure the horizontal XY-coordinates at the top of rod and the
        vertical Z-coordinates at the top the rod, the ground surface and the bottom of the
        rod over time.

        Returns
        -------
        plt.Figure
        """
        fig, axes = plt.subplots(3, 1, figsize=(10, 30), sharex=True)

        fig.suptitle(f"Spatial measurements for object: {self.object_id}")

        self.plot_x_time(axes[0])
        axes[0].set_title("Horizontal X")

        self.plot_y_time(axes[1])
        axes[1].set_title("Horizontal Y")

        self.plot_z_time(axes[2])
        axes[2].set_title("Vertical Z")

        return fig

    def plot_xy_plan_view(self, axes: Axes | None = None) -> Axes:
        """
        Plot the plan view of the horizontal XY coordinates
        at the top of the rod.

        Parameters
        ----------
        axes: plt.Axes
            Axes to create the figure

        Returns
        -------
        plt.Axes
        """
        if axes is not None:
            if not isinstance(axes, Axes):
                raise TypeError("Expected 'Axes' type or None for 'axes' parameter.")

        if axes is None:
            axes = plt.gca()

        df = self.to_dataframe()

        axes.plot(df["rod_top_x"], df["rod_top_y"])

        # Mark the start and end of the measurements.
        axes.plot(
            df["rod_top_x"].iloc[0],
            df["rod_top_y"].iloc[0],
            marker="*",
            color="black",
            label="start",
        )

        axes.plot(
            df["rod_top_x"].iloc[-1],
            df["rod_top_y"].iloc[-1],
            marker="+",
            color="red",
            label="end",
        )

        axes.legend(loc="upper right")

        axes.set_xlim(df["rod_top_x"].min() - 0.5, df["rod_top_x"].max() + 0.5)
        axes.set_ylim(df["rod_top_y"].min() - 0.5, df["rod_top_y"].max() + 0.5)
        axes.grid()

        axes.set_xlabel(f"X [{self.coordinate_reference_systems.horizontal_units}]")
        axes.set_ylabel(f"Y [{self.coordinate_reference_systems.horizontal_units}]")
        axes.set_title(
            f"Plan view of horizonal measurements at rod top for object: {self.object_id}"
        )

        return axes
