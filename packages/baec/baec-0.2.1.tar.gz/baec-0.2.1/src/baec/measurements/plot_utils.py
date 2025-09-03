from __future__ import annotations

import datetime

from matplotlib.axes import Axes


def validate_plot_parameter_axes(axes: Axes | None) -> None:
    """
    Private method to validate the 'axes' parameter of the plot methods.
    """
    if axes is not None and not isinstance(axes, Axes):
        raise TypeError(
            "Expected 'Axes' type or None for 'axes' parameter, but got {type(axes)}."
        )


def validate_plot_parameter_log_time(log_time: bool) -> None:
    """
    Private method to validate the 'log_time' parameter of the plot methods.
    """
    if not isinstance(log_time, bool):
        raise TypeError(
            f"Expected 'bool' type for 'log_time' parameter, but got {type(log_time)}."
        )


def validate_plot_parameter_min_log_time(min_log_time: float) -> None:
    """
    Private method to validate the 'min_log_time' parameter of the plot methods.
    """
    if not isinstance(min_log_time, (int, float)):
        raise TypeError(
            f"Expected 'float' type for 'min_log_time' parameter, but got {type(min_log_time)}."
        )

    if min_log_time <= 0.0:
        raise ValueError("The 'min_log_time' parameter must be greater than 0.0.")


def validate_plot_parameter_add_date_time(add_date_time: bool) -> None:
    """
    Private method to validate the 'add_date_time' parameter of the plot methods.
    """
    if not isinstance(add_date_time, bool):
        raise TypeError(
            f"Expected 'bool' type for 'add_date_time' parameter, but got {type(add_date_time)}."
        )


def validate_plot_parameter_datetime_format(datetime_format: str) -> None:
    """
    Private method to validate the 'datetime_format' parameter of the plot methods.
    """
    if not isinstance(datetime_format, str):
        raise TypeError(
            f"Expected 'str' type for 'datetime_format' parameter, but got {type(datetime_format)}."
        )

    try:
        datetime.datetime.now().strftime(datetime_format)
    except ValueError:
        raise ValueError(
            "The 'datetime_format' parameter is not a valid format for the strftime method "
            + "of the datetime.datetime class."
        )
