from __future__ import annotations

import datetime
from functools import cache, cached_property
from typing import List

from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    SettlementRodMeasurementStatus,
    StatusMessage,
)
from baec.project import Project


class MeasuredSettlement:
    """
    Represents the measured settlement derived from a single settlement rod measurement.
    It includes the thickness of the fill layer and the x and y displacements at the rod top.
    """

    def __init__(
        self,
        project: Project,
        object_id: str,
        start_date_time: datetime.datetime,
        date_time: datetime.datetime,
        fill_thickness: float,
        settlement: float,
        x_displacement: float,
        y_displacement: float,
        horizontal_units: str,
        vertical_units: str,
        status: SettlementRodMeasurementStatus,
        status_messages: List[StatusMessage],
    ) -> None:
        """
        Initializes a MeasuredSettlement object.

        Parameters
        ----------
        project : Project
            The project which the measured settlement belongs to.
        object_id : str
            The ID of the measured object.
        start_date_time : datetime.datetime
            The date and time of the start of the measurements (zero measurement).
        date_time : datetime.datetime
            The date and time of the measured settlement.
        fill_thickness : float
            The thickness of the fill layer.
            Units are according to `vertical_units`.
        settlement : float
            The settlement of the initial ground profile relative to the zero measurement.
            A positive (+) settlement value represents a downward movement.
            Units are according to `vertical_units`.
        x_displacement : float
            The horizontal X-displacement relative to the zero measurement.
            Units are according to the `horizontal_units`.
        y_displacement : float
            The horizontal Y-displacement relative to the zero measurement.
            Units are according to the `horizontal_units`.
        horizontal_units: str
            The units of the horizontal XY displacements.
        vertical_units: str
            The units of the measurements and distances in the vertical direction.
        status: SettlementRodMeasurementStatus
            The status of the settlement rod measurement from which the measured settlement
            is derived.
        status_messages: List[StatusMessage]
            The list of status messages about the settlement rod measurement from which the
            measured settlement is derived.

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If empty string for `object_id`, `horizontal_units` and `vertical_units`.
            If `date_time` is not >= `start_date_time`.
            If negative value for `fill_thickness`.
        """

        # Initialize all attributes using private setters.
        self._set_project(project)
        self._set_object_id(object_id)
        self._set_start_date_time(start_date_time)
        self._set_date_time(date_time)
        self._set_fill_thickness(fill_thickness)
        self._set_settlement(settlement)
        self._set_x_displacement(x_displacement)
        self._set_y_displacement(y_displacement)
        self._set_horizontal_units(horizontal_units)
        self._set_vertical_units(vertical_units)
        self._set_status(status)
        self._set_status_messages(status_messages)

    @classmethod
    def from_settlement_rod_measurement(
        cls,
        measurement: SettlementRodMeasurement,
        zero_measurement: SettlementRodMeasurement,
    ) -> MeasuredSettlement:
        """
        Create a MeasuredSettlement object from a measurement and a zero measurement.

        Parameters
        ----------
        measurement : SettlementRodMeasurement
            The measurement to be interpreted.
        zero_measurement : SettlementRodMeasurement
            The measurement considered to the the zero measurement.

        Returns
        -------
        MeasuredSettlement
            The derived MeasuredSettlement object relative to the zero measurement.

        Raises
        ------
            TypeError
                If the types are incorrect.
            ValueError
                If the measurements do not belong to the same project, object_id or coordinate
                reference systems.
        """

        # Check types are correct
        if not isinstance(measurement, SettlementRodMeasurement):
            raise TypeError(
                "Expected 'SettlementRodMeasurement' type for 'measurement'."
            )

        if not isinstance(zero_measurement, SettlementRodMeasurement):
            raise TypeError(
                "Expected 'SettlementRodMeasurement' type for 'zero_measurement'."
            )

        # Check if both measurements belong to the same project, object and coordinate
        # reference systems.
        if measurement.project != zero_measurement.project:
            raise ValueError("Both measurements must belong to the same project.")

        if measurement.object_id != zero_measurement.object_id:
            raise ValueError("Both measurements must belong to the same object.")

        if (
            measurement.coordinate_reference_systems
            != zero_measurement.coordinate_reference_systems
        ):
            raise ValueError(
                "Both measurements must have the same coordinate reference systems."
            )

        return cls(
            project=measurement.project,
            object_id=measurement.object_id,
            start_date_time=zero_measurement.date_time,
            date_time=measurement.date_time,
            fill_thickness=measurement.ground_surface_z - measurement.rod_bottom_z,
            settlement=zero_measurement.rod_bottom_z - measurement.rod_bottom_z,
            x_displacement=measurement.rod_top_x - zero_measurement.rod_top_x,
            y_displacement=measurement.rod_top_y - zero_measurement.rod_top_y,
            horizontal_units=measurement.coordinate_reference_systems.horizontal_units,
            vertical_units=measurement.coordinate_reference_systems.vertical_units,
            status=measurement.status,
            status_messages=measurement.status_messages,
        )

    def _set_project(self, value: Project) -> None:
        """
        Private setter for project attribute.
        """
        if not isinstance(value, Project):
            raise TypeError("Expected 'Project' type for 'project' attribute.")
        self._project = value

    def _set_object_id(self, value: str) -> None:
        """
        Private setter for object_id attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'object_id' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'object_id' attribute.")
        self._object_id = value

    def _set_start_date_time(self, value: datetime.datetime) -> None:
        """
        Private setter for start_date_time attribute.
        """
        if not isinstance(value, datetime.datetime):
            raise TypeError(
                "Expected 'datetime.datetime' type for 'start_date_time' attribute."
            )
        self._start_date_time = value

    def _set_date_time(self, value: datetime.datetime) -> None:
        """
        Private setter for date_time attribute.
        """
        if not isinstance(value, datetime.datetime):
            raise TypeError(
                "Expected 'datetime.datetime' type for 'date_time' attribute."
            )
        if not value >= self.start_date_time:
            raise ValueError("Value of 'date_time' must be >= 'start_date_time'.")
        self._date_time = value

    def _set_fill_thickness(self, value: float) -> None:
        """
        Private setter for fill_thickness attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'fill_thickness' attribute.")
        if value < 0:
            raise ValueError(
                "Negative value not allowed for 'fill_thickness' attribute."
            )
        self._fill_thickness = value

    def _set_settlement(self, value: float) -> None:
        """
        Private setter for settlement attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'settlement' attribute.")
        self._settlement = value

    def _set_x_displacement(self, value: float) -> None:
        """
        Private setter for x_displacement attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'x_displacement' attribute.")
        self._x_displacement = value

    def _set_y_displacement(self, value: float) -> None:
        """
        Private setter for y_displacement attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'y_displacement' attribute.")
        self._y_displacement = value

    def _set_horizontal_units(self, value: str) -> None:
        """
        Private setter for horizontal_units attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'horizontal_units' attribute.")
        if value == "":
            raise ValueError(
                "Empty string not allowed for 'horizontal_units' attribute."
            )
        self._horizontal_units = value

    def _set_vertical_units(self, value: str) -> None:
        """
        Private setter for vertical_units attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'vertical_units' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'vertical_units' attribute.")
        self._vertical_units = value

    def _set_status(self, value: SettlementRodMeasurementStatus) -> None:
        """
        Private setter for status attribute.
        """
        if not isinstance(value, SettlementRodMeasurementStatus):
            raise TypeError(
                "Expected 'SettlementRodMeasurementStatus' type for 'status' attribute."
            )
        self._status = value

    def _set_status_messages(self, value: List[StatusMessage]) -> None:
        """
        Private setter for status attribute.
        """
        if not isinstance(value, list):
            raise TypeError(
                "Expected 'List[StatusMessage]' type for 'status_messages' attribute."
            )
        # Check if the input is a list of StatusMessage objects.
        if not all(isinstance(item, StatusMessage) for item in value):
            raise TypeError(
                "Expected 'List[StatusMessage]' type for 'status_messages' attribute."
            )
        self._status_messages = value

    @property
    def project(self) -> Project:
        """
        The project which the measured settlement belongs to.
        """
        return self._project

    @property
    def object_id(self) -> str:
        """
        The ID of the measured object.
        """
        return self._object_id

    @property
    def start_date_time(self) -> datetime.datetime:
        """
        The date and time of the start of the measurements (zero measurement).
        """
        return self._start_date_time

    @property
    def date_time(self) -> datetime.datetime:
        """
        The date and time of the measured settlement.
        """
        return self._date_time

    @cached_property
    def days(self) -> float:
        """
        The time elapsed since the zero measurement in [days].
        """
        return (self.date_time - self.start_date_time).total_seconds() / 86400.0

    @property
    def fill_thickness(self) -> float:
        """
        The thickness of the fill layer.
        Units are according to `vertical_units`.
        """
        return self._fill_thickness

    @property
    def settlement(self) -> float:
        """
        The settlement of the initial ground profile relative to the zero measurement.
        A positive (+) settlement value represents a downward movement.
        Units are according to `vertical_units`.
        """
        return self._settlement

    @property
    def x_displacement(self) -> float:
        """
        The horizontal X-displacement at the rod top relative to the zero measurement.
        Units are according to the `horizontal_units`.
        """
        return self._x_displacement

    @property
    def y_displacement(self) -> float:
        """
        The horizontal Y-displacement at the rod top relative to the zero measurement.
        Units are according to the `horizontal_units`.
        """
        return self._y_displacement

    @property
    def horizontal_units(self) -> str:
        """
        The units of the horizontal XY displacements.
        """
        return self._horizontal_units

    @property
    def vertical_units(self) -> str:
        """
        The units of the measurements and distances in the vertical direction.
        """
        return self._vertical_units

    @property
    def status(self) -> SettlementRodMeasurementStatus:
        """
        The status of the settlement rod measurement from which the measured settlement
        is derived.
        """
        return self._status

    @property
    def status_messages(self) -> List[StatusMessage]:
        """
        The list of status messages about the settlement rod measurement from which the
        measured settlement is derived.
        """
        return self._status_messages

    @cache
    def to_dict(self) -> dict:
        """
        Convert the measured settlement to a dictionary.
        """
        return {
            "project_id": self.project.id,
            "project_name": self.project.name,
            "object_id": self.object_id,
            "start_date_time": self.start_date_time,
            "date_time": self.date_time,
            "days": self.days,
            "fill_thickness": self.fill_thickness,
            "settlement": self.settlement,
            "x_displacement": self.x_displacement,
            "y_displacement": self.y_displacement,
            "horizontal_units": self.horizontal_units,
            "vertical_units": self.vertical_units,
            "status": self.status.value,
            "status_messages": "\n".join([m.to_string() for m in self.status_messages]),
        }
