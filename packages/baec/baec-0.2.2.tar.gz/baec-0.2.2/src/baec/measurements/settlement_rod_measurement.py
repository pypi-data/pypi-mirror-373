from __future__ import annotations

import datetime
from enum import Enum
from functools import cache, cached_property, total_ordering
from typing import List

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.project import Project


class SettlementRodMeasurementStatus(Enum):
    """Represents the status of a settlement rod measurement."""

    """If the highest severity level of the status messages is "OK".
    This will indicate that the measurement is correct."""
    OK = "OK"

    """If the highest severity level of the status messages is "INFO".
    This will indicate that there is still at least one informative comment about the measurement. The measurement is still correct."""
    INFO = "INFO"

    """If the highest severity level of the status messages is "WARNING".
    This will indicate that there is still at least one warning about the measurement. The measurement may not be correct or accurate enough."""
    WARNING = "WARNING"

    """If the highest severity level of the status messages is "ERROR".
    This will indicate that there is still at least one error about the measurement. The measurement is most probably incorrect."""
    ERROR = "ERROR"


@total_ordering
class StatusMessageLevel(Enum):
    """Represents the severity level of a status message."""

    """Measurement is correct."""
    OK = "OK"

    """Measurement has an informative comment. The measurement is still correct."""
    INFO = "INFO"

    """Measurement has a warning. The measurement may not be correct or accurate enough."""
    WARNING = "WARNING"

    """Measurement has an error. The measurement is most probably incorrect."""
    ERROR = "ERROR"

    def __lt__(self, other: object) -> bool:
        """
        Compares the order of the status message level.
        """
        if isinstance(other, StatusMessageLevel):
            return self.order() < other.order()
        return False

    def order(self) -> int:
        """
        Returns the order of the status message level.
        """
        order = {
            StatusMessageLevel.OK: 0,
            StatusMessageLevel.INFO: 1,
            StatusMessageLevel.WARNING: 2,
            StatusMessageLevel.ERROR: 3,
        }
        return order[self]


class StatusMessage:
    """
    Represents a status message of a single settlement rod measurement.
    """

    def __init__(
        self,
        code: int,
        description: str,
        level: StatusMessageLevel,
    ):
        """
        Initializes a StatusMessage object.

        Parameters
        ----------
        code : int
            The code of the status message.
        description : str
            The description of the status message.
        level : StatusMessageLevel
            The severity level of the status message.
        """

        # Initialize all attributes using private setters.
        self._set_code(code)
        self._set_description(description)
        self._set_level(level)

    def _set_code(self, value: int) -> None:
        """
        Private setter for code attribute.
        """
        if not isinstance(value, int):
            raise TypeError("Expected 'int' type for 'code' attribute.")
        self._code = value

    def _set_description(self, value: str) -> None:
        """
        Private setter for description attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'description' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'description' attribute.")
        self._description = value

    def _set_level(self, value: StatusMessageLevel) -> None:
        """
        Private setter for level attribute.
        """
        if not isinstance(value, StatusMessageLevel):
            raise TypeError("Expected 'StatusMessageLevel' type for 'level' attribute.")
        self._level = value

    @cache
    def to_string(self) -> str:
        """
        Convert the status message to a string.
        """
        return f"(code={self.code}, description={self.description}, level={self.level.value})"

    @property
    def code(self) -> int:
        """
        The code of the status message.
        """
        return self._code

    @property
    def description(self) -> str:
        """
        The description of the status message.
        """
        return self._description

    @property
    def level(self) -> StatusMessageLevel:
        """
        The severity level of the status message.
        """
        return self._level


class SettlementRodMeasurement:
    """
    Represents a single settlement rod measurement.
    """

    def __init__(
        self,
        project: Project,
        device: MeasurementDevice,
        object_id: str,
        date_time: datetime.datetime,
        coordinate_reference_systems: CoordinateReferenceSystems,
        rod_top_x: float,
        rod_top_y: float,
        rod_top_z: float,
        rod_length: float,
        rod_bottom_z: float,
        ground_surface_z: float,
        status_messages: List[StatusMessage],
        temperature: float | None = None,
        voltage: float | None = None,
    ) -> None:
        """
        Initializes a SettlementRodMeasurement object.

        Parameters
        ----------
        project : Project
            The project which the measurement belongs to.
        device : MeasurementDevice
            The measurement device.
        object_id : str
            The ID of the measured object.
        date_time : datetime.datetime
            The date and time of the measurement.
        coordinate_reference_systems : CoordinateReferenceSystems
            The horizontal (X, Y) and vertical (Z) coordinate reference systems (CRS) of the
            spatial measurements.
        rod_top_x : float
            The horizontal X-coordinate of the top of the settlement rod.
            Units are according to the `coordinate_reference_systems`.
        rod_top_y : float
            The horizontal Y-coordinate of the top of the settlement rod.
            Units are according to the `coordinate_reference_systems`.
        rod_top_z : float
            The vertical Z-coordinate of the top of the settlement rod.
            It is the top of the settlement rod.
            Units and datum are according to the `coordinate_reference_systems`.
        rod_length : float
            The length of the settlement rod including the thickness of the settlement plate.
            It is in principle the vertical distance between the top of the settlement rod and
            the bottom of the settlement plate.
            Units are according to the `coordinate_reference_systems`.
        rod_bottom_z : float
            The corrected Z-coordinate at the bottom of the settlement rod (coincides with bottom of settlement plate).
            Note that the bottom of the plate is in principle the original ground surface.
            Units and datum according to the `coordinate_reference_systems`.
        ground_surface_z : float
            The Z-coordinate of the ground surface.
            It is in principle the top of the fill, if present.
            Units and datum according to the `coordinate_reference_systems`.
        status_messages: List[StatusMessage]
            The list of status messages about the measurement.
        temperature : float or None, optional
            The temperature at the time of measurement in [°C], or None if unknown (default: None).
        voltage : float or None, optional
            The voltage measured in [mV], or None if unknown (default: None).

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If empty string for `object_id`.
            If negative value for `rod_length`.
        """

        # Initialize all attributes using private setters.
        self._set_project(project)
        self._set_device(device)
        self._set_object_id(object_id)
        self._set_date_time(date_time)
        self._set_coordinate_reference_systems(coordinate_reference_systems)
        self._set_rod_top_x(rod_top_x)
        self._set_rod_top_y(rod_top_y)
        self._set_rod_top_z(rod_top_z)
        self._set_rod_length(rod_length)
        self._set_rod_bottom_z(rod_bottom_z)
        self._set_ground_surface_z(ground_surface_z)
        self._set_status_messages(status_messages)
        self._set_temperature(temperature)
        self._set_voltage(voltage)

    def _set_project(self, value: Project) -> None:
        """
        Private setter for project attribute.
        """
        if not isinstance(value, Project):
            raise TypeError("Expected 'Project' type for 'project' attribute.")
        self._project = value

    def _set_device(self, value: MeasurementDevice) -> None:
        """
        Private setter for device attribute.
        """
        if not isinstance(value, MeasurementDevice):
            raise TypeError("Expected 'MeasurementDevice' type for 'device' attribute.")
        self._device = value

    def _set_object_id(self, value: str) -> None:
        """
        Private setter for object_id attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'object_id' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'object_id' attribute.")
        self._object_id = value

    def _set_date_time(self, value: datetime.datetime) -> None:
        """
        Private setter for date_time attribute.
        """
        if not isinstance(value, datetime.datetime):
            raise TypeError(
                "Expected 'datetime.datetime' type for 'date_time' attribute."
            )
        self._date_time = value

    def _set_coordinate_reference_systems(
        self, value: CoordinateReferenceSystems
    ) -> None:
        """
        Private setter for coordinate_reference_systems attribute.
        """
        if not isinstance(value, CoordinateReferenceSystems):
            raise TypeError(
                "Expected 'CoordinateReferenceSystems' type for 'coordinate_reference_systems' attribute."
            )
        self._coordinate_reference_systems = value

    def _set_rod_top_x(self, value: float) -> None:
        """
        Private setter for rod_top_x attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'rod_top_x' attribute.")
        self._rod_top_x = value

    def _set_rod_top_y(self, value: float) -> None:
        """
        Private setter for rod_top_y attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type 'rod_top_y' attribute.")
        self._rod_top_y = value

    def _set_rod_top_z(self, value: float) -> None:
        """
        Private setter for rod_top_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'rod_top_z' attribute.")
        self._rod_top_z = value

    def _set_rod_length(self, value: float) -> None:
        """
        Private setter for rod_length attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'rod_length' attribute.")
        if value < 0:
            raise ValueError("Negative value not allowed for 'rod_length' attribute.")
        self._rod_length = value

    def _set_rod_bottom_z(self, value: float) -> None:
        """
        Private setter for rod_bottom_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'rod_bottom_z' attribute.")
        self._rod_bottom_z = value

    def _set_ground_surface_z(self, value: float) -> None:
        """
        Private setter for ground_surface_z attribute.
        """
        if isinstance(value, int):
            value = float(value)
        if not isinstance(value, float):
            raise TypeError("Expected 'float' type for 'ground_surface_z' attribute.")
        self._ground_surface_z = value

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

    def _set_temperature(self, value: float | None) -> None:
        """
        Private setter for temperature attribute.
        """
        if value is not None:
            if isinstance(value, int):
                value = float(value)
            if not isinstance(value, float):
                raise TypeError(
                    "Expected 'float' or 'None' type for 'temperature' attribute."
                )
        self._temperature = value

    def _set_voltage(self, value: float | None) -> None:
        """
        Private setter for voltage attribute.
        """
        if value is not None:
            if isinstance(value, int):
                value = float(value)
            if not isinstance(value, float):
                raise TypeError(
                    "Expected 'float' or 'None' type for 'voltage' attribute."
                )
        self._voltage = value

    @property
    def project(self) -> Project:
        """
        The project which the measurement belongs to.
        """
        return self._project

    @property
    def device(self) -> MeasurementDevice:
        """
        The measurement device.
        """
        return self._device

    @property
    def object_id(self) -> str:
        """
        The ID of the measured object.
        """
        return self._object_id

    @property
    def date_time(self) -> datetime.datetime:
        """
        The date and time of the measurement.
        """
        return self._date_time

    @property
    def coordinate_reference_systems(self) -> CoordinateReferenceSystems:
        """
        The horizontal (X, Y) and vertical (Z) coordinate reference systems (CRS) of the
        spatial measurements.
        """
        return self._coordinate_reference_systems

    @property
    def rod_top_x(self) -> float:
        """
        The horizontal X-coordinate of the top of the settlement rod.
        Units are according to the `coordinate_reference_system`.
        """
        return self._rod_top_x

    @property
    def rod_top_y(self) -> float:
        """
        The horizontal Y-coordinate of the top of the settlement rod.
        Units are according to the `coordinate_reference_system`.
        """
        return self._rod_top_y

    @property
    def rod_top_z(self) -> float:
        """
        The vertical Z-coordinate of the top of the settlement rod.
        It is the top of the settlement rod.
        Units are according to the `coordinate_reference_system`.
        """
        return self._rod_top_z

    @property
    def rod_length(self) -> float:
        """
        The length of the settlement rod including the thickness of the settlement plate.
        It is in principle the vertical distance between the top of the settlement rod and the bottom of the settlement plate.
        Units are according to the `coordinate_reference_system`.
        """
        return self._rod_length

    @property
    def rod_bottom_z(self) -> float:
        """
        The corrected Z-coordinate at the bottom of the settlement rod (coincides with bottom of settlement plate).
        Note that the bottom of the plate is in principle the original ground surface.
        Units are according to the `coordinate_reference_system`.
        """
        return self._rod_bottom_z

    @property
    def rod_bottom_z_uncorrected(self) -> float:
        """
        The uncorrected Z-coordinate at the bottom of the settlement rod (coincides with bottom of settlement plate).
        It is computed as the difference beteen the Z-coordinate of the top of the settlement rod and the rod length.
        Units are according to the `coordinate_reference_system`.
        """
        return self.rod_top_z - self.rod_length

    @property
    def ground_surface_z(self) -> float:
        """
        The Z-coordinate of the ground surface.
        It is in principle the top of the fill, if present.
        """
        return self._ground_surface_z

    @property
    def status_messages(self) -> List[StatusMessage]:
        """
        The list of status messages about the measurement.
        """
        return self._status_messages

    @cached_property
    def status(self) -> SettlementRodMeasurementStatus:
        """
        The status of the measurement.
        """

        # If no status messages are available, return OK.
        if len(self.status_messages) == 0:
            return SettlementRodMeasurementStatus.OK

        # Get the highest severity level of the status messages.
        highest_level = max([message.level for message in self.status_messages])

        # Return the corresponding status.
        if highest_level == StatusMessageLevel.OK:
            return SettlementRodMeasurementStatus.OK
        elif highest_level == StatusMessageLevel.INFO:
            return SettlementRodMeasurementStatus.INFO
        elif highest_level == StatusMessageLevel.WARNING:
            return SettlementRodMeasurementStatus.WARNING
        elif highest_level == StatusMessageLevel.ERROR:
            return SettlementRodMeasurementStatus.ERROR
        else:
            raise ValueError(
                f"No corresponding SettlementRodMeasurementStatus is available for {highest_level}."
            )

    @property
    def temperature(self) -> float | None:
        """
        The temperature at the time of measurement in [°C], or None if unknown.
        """
        return self._temperature

    @property
    def voltage(self) -> float | None:
        """
        The voltage measured in [mV], or None if unknown.
        """
        return self._voltage

    @cache
    def to_dict(self) -> dict:
        """
        Convert the measurement to a dictionary.
        """
        return {
            "project_id": self.project.id,
            "project_name": self.project.name,
            "device_id": self.device.id,
            "device_qr_code": self.device.qr_code,
            "object_id": self.object_id,
            "coordinate_horizontal_epsg_code": self.coordinate_reference_systems.horizontal.to_epsg(),
            "coordinate_vertical_epsg_code": self.coordinate_reference_systems.vertical.to_epsg(),
            "coordinate_horizontal_units": self.coordinate_reference_systems.horizontal_units,
            "coordinate_vertical_units": self.coordinate_reference_systems.vertical_units,
            "coordinate_vertical_datum": self.coordinate_reference_systems.vertical_datum,
            "date_time": self.date_time,
            "rod_top_x": self.rod_top_x,
            "rod_top_y": self.rod_top_y,
            "rod_top_z": self.rod_top_z,
            "rod_length": self.rod_length,
            "rod_bottom_z": self.rod_bottom_z,
            "rod_bottom_z_uncorrected": self.rod_bottom_z_uncorrected,
            "ground_surface_z": self.ground_surface_z,
            "status": self.status.value,
            "status_messages": "\n".join([m.to_string() for m in self.status_messages]),
            "temperature": self.temperature,
            "voltage": self.voltage,
        }
