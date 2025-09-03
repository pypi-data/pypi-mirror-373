import pytest

from baec.project import Project


def test_project_with_valid_input() -> None:
    """Test initialization of Project with valid input."""
    project = Project(id_="P001", name="name_1")
    assert project.id == "P001"
    assert project.name == "name_1"


def test_project_init_with_invalid_id() -> None:
    """Test initialization of Project with invalid ID."""
    # Invalid id: None
    with pytest.raises(TypeError, match="id"):
        Project(id_=None, name="name_1")

    # Invalid id: Empty string
    with pytest.raises(ValueError, match="id"):
        Project(id_="", name="name_1")


def test_project_init_with_invalid_name() -> None:
    """Test initialization of Project with invalid name."""
    # Invalid name: None
    with pytest.raises(TypeError, match="name"):
        Project(id_="P001", name=None)

    # Invalid name: Empty string
    with pytest.raises(ValueError, match="name"):
        Project(id_="P001", name="")


def test_project__eq__method() -> None:
    """Test the __eq__ method of Project."""
    project_1 = Project(id_="P001", name="name_1")
    project_2 = Project(id_="P001", name="name_1")
    project_3 = Project(id_="P002", name="name_2")
    project_4 = Project(id_="P002", name="name_1")

    assert project_1 == project_2
    assert project_1 != project_3
    assert project_1 != project_4
    assert project_2 != project_3
    assert project_3 != project_4

    assert project_1 == project_1
    assert project_1 != None
    assert project_1 != "P001"
