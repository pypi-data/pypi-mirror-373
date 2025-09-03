from __future__ import annotations


class Project:
    """
    Represents a project.
    """

    def __init__(
        self,
        id_: str,
        name: str,
    ) -> None:
        """
        Initializes a MeasurementDevice object.

        Parameters
        ----------
        id_ : str
            The ID of the project.
        name : str
            The name of the project.

        Raises
        ------
        TypeError
            If the input types are incorrect.
        ValueError
            If empty string for `id_` or `name`.
        """

        # Initialize all attributes using private setters.
        self._set_id(id_)
        self._set_name(name)

    def _set_id(self, value: str) -> None:
        """
        Private setter for id attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'id' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'id' attribute.")
        self._id = value

    def _set_name(self, value: str) -> None:
        """
        Private setter for name attribute.
        """
        if not isinstance(value, str):
            raise TypeError("Expected 'str' type for 'name' attribute.")
        if value == "":
            raise ValueError("Empty string not allowed for 'name' attribute.")
        self._name = value

    @property
    def id(self) -> str:
        """
        The ID of the project.
        """
        return self._id

    @property
    def name(self) -> str:
        """
        The name of the project.
        """
        return self._name

    def __eq__(self, other: object) -> bool:
        """
        Check if two MeasurementDevice objects are equal.
        It compares the `id` attribute and `name` attribute.

        Parameters
        ----------
        other : object
            The object to compare.

        Returns
        -------
        bool
            True if the objects are equal, False otherwise.
        """
        if not isinstance(other, Project):
            return False
        return self.id == other.id and self.name == other.name
