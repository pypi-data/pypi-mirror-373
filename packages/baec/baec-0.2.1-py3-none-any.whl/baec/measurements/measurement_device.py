from __future__ import annotations


class MeasurementDevice:
    """
    Represents a measurement device.
    """

    def __init__(
        self,
        id_: str,
        qr_code: str | None = None,
    ) -> None:
        """
        Initializes a MeasurementDevice object.

        Parameters
        ----------
        id_ : str
            The ID of the measurement device.
        qr_code : str | None, optional
            The QR code of the measurement device, or None if unknown (default: None).

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If empty string for `id_` or `qr_code`.
        """

        # Initialize all attributes using private setters.
        self._set_id(id_)
        self._set_qr_code(qr_code)

    def _set_id(self, value: str) -> None:
        """
        Private setter for id attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'id' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'id' attribute.")
        self._id = value

    def _set_qr_code(self, value: str | None) -> None:
        """
        Private setter for qr_code attribute.
        """
        if value is not None:
            if not isinstance(value, str):
                raise TypeError(
                    "Expected 'str' or 'None' type for 'qr_code' attribute."
                )
        if value == "":
            raise ValueError("Empty string not allowed for 'qr_code' attribute.")
        self._qr_code = value

    @property
    def id(self) -> str:
        """
        The ID of the measurement device.
        """
        return self._id

    @property
    def qr_code(self) -> str | None:
        """
        The QR-code of the measurement device.
        """
        return self._qr_code

    def __eq__(self, other: object) -> bool:
        """
        Check if two MeasurementDevice objects are equal.
        It compares the `id` attribute.

        Parameters
        ----------
        other : object
            The object to compare.

        Returns
        -------
        bool
            True if the objects are equal, False otherwise.
        """
        if not isinstance(other, MeasurementDevice):
            return False
        return self.id == other.id
