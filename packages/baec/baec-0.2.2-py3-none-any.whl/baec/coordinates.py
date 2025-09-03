from __future__ import annotations

from functools import cached_property

import pyproj


class CoordinateReferenceSystems:
    """
    Represents the horizontal (X, Y) and vertical (Z) coordinate reference systems of a 3D point.
    """

    def __init__(self, horizontal: pyproj.CRS, vertical: pyproj.CRS) -> None:
        """
        Initializes a CoordinateReferenceSystems object.

        Parameters
        ----------
        horizontal : pyproj.CRS
            The coordinate reference system of the X and Y-coordinates.
            It is a `pyproj.CRS` object (see https://pyproj4.github.io/pyproj/stable/api/crs/crs.html) of
            type 'Projected' or 'Compound'.
        vertical : pyproj.CRS
            The coordinate reference system of the Z-coordinate.
            It is a `pyproj.CRS` object (see https://pyproj4.github.io/pyproj/stable/api/crs/crs.html) of
            type 'Vertical' or 'Compound'.

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If `horizontal` is not a projected or compound CRS.
            If `vertical` is not a vertical or compound CRS.
        """

        # Initialize all attributes using private setters.
        self._set_horizontal(horizontal)
        self._set_vertical(vertical)

    @classmethod
    def from_epsg(cls, horizontal: int, vertical: int) -> CoordinateReferenceSystems:
        """
        Creates a CoordinateReferenceSystems object from the EPSG codes of the horizontal and vertical CRS.

        Note
        ----
        If your settlement rod is located in the Netherlands the horizontal coordinate reference systems is likely `28992`
        (Amersfoort / RD New) and the vertical `5709` (NAP height). To combine use `7415` (Amersfoort / RD New + NAP height).

        Parameters
        ----------
        horizontal : int
            The EPSG code of the horizontal CRS.
        vertical : int
            The EPSG code of the vertical CRS.

        Returns
        -------
        CoordinateReferenceSystems
            A CoordinateReferenceSystems object with the horizontal and vertical CRS.

        Raises
        ------
        pyproj.exceptions.CRSError
            If the EPSG codes are not valid.
        """
        return cls(
            horizontal=pyproj.CRS.from_epsg(horizontal),
            vertical=pyproj.CRS.from_epsg(vertical),
        )

    def _set_horizontal(self, value: pyproj.CRS) -> None:
        """
        Private setter for horizontal attribute.
        """
        if not isinstance(value, pyproj.CRS):
            raise TypeError("Expected 'pyproj.CRS' type for 'horizontal' attribute.")

        # Check whether the CRS is a projected or compound CRS.
        if not value.is_projected and not value.is_compound:
            raise ValueError(
                "Expected 'is_projected' or 'is_compound' to be true for 'horizontal' attribute."
            )

        # Set the coordinate system in case of a projected CRS.
        if value.is_projected:
            self._horizontal = value
        # Set the coordinate system in case of a compound CRS.
        elif value.is_compound:
            projected_crs = None
            for crs in value.sub_crs_list:
                if crs.is_projected:
                    projected_crs = crs
                    break
            if projected_crs is None:
                raise ValueError("No projected CRS found in the compound CRS.")
            self._horizontal = projected_crs

    def _set_vertical(self, value: pyproj.CRS) -> None:
        """
        Private setter for z attribute.
        """
        if not isinstance(value, pyproj.CRS):
            raise TypeError("Expected 'pyproj.CRS' type for 'vertical' attribute.")

        # Check whether the CRS is a vertical or compound CRS.
        if not value.is_vertical and not value.is_compound:
            raise ValueError(
                "Expected 'is_vertical' or 'is_compound' to be true for 'vertical' attribute."
            )

        # Set the coordinate system in case of a vertical CRS.
        if value.is_vertical:
            self._vertical = value
        # Set the coordinate system in case of a compound CRS.
        elif value.is_compound:
            vertical_crs = None
            for crs in value.sub_crs_list:
                if crs.is_vertical:
                    vertical_crs = crs
                    break
            if vertical_crs is None:
                raise ValueError("No vertical CRS found in the compound CRS.")
            self._vertical = vertical_crs

    @property
    def horizontal(self) -> pyproj.CRS:
        """
        The coordinate reference system of the horizontal X and Y-coordinates.
        """
        return self._horizontal

    @property
    def vertical(self) -> pyproj.CRS:
        """
        The coordinate reference system of the vertical Z-coordinate.
        """
        return self._vertical

    @property
    def horizontal_units(self) -> str:
        """
        The units of the horizontal CRS.
        """
        return self._horizontal.axis_info[0].unit_name

    @property
    def vertical_units(self) -> str:
        """
        The units of the vertical CRS
        """
        return self._vertical.axis_info[0].unit_name

    @property
    def vertical_datum(self) -> str:
        """
        The name of the vertical datum.
        """
        return self._vertical.name

    @cached_property
    def vertical_datum_and_units(self) -> str:
        """
        The vertical datum and units of the vertical CRS.
        """
        return f"{self.vertical_datum} [{self.vertical_units}]"

    def __str__(self) -> str:
        """Converts the object to a string."""
        return f"CoordinateReferenceSystems(Horizontal: {self.horizontal.to_epsg()}, Vertical: {self.vertical.to_epsg()})"

    def __eq__(self, value: object) -> bool:
        """Compares two CoordinateReferenceSystems objects."""
        if not isinstance(value, CoordinateReferenceSystems):
            return False
        return self.horizontal.equals(value.horizontal) and self.vertical.equals(
            value.vertical
        )
