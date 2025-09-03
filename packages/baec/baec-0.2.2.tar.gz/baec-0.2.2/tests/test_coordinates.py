import pyproj
import pytest

from baec.coordinates import CoordinateReferenceSystems


def test_coordinate_reference_system_init_with_valid_input() -> None:
    """Test initialization of CoordinateReferenceSystems with valid input."""

    # With projected and vertical CRS
    horizontal_crs = pyproj.CRS.from_epsg(28992)
    vertical_crs = pyproj.CRS.from_epsg(5710)
    crs = CoordinateReferenceSystems(horizontal=horizontal_crs, vertical=vertical_crs)
    assert crs.horizontal == horizontal_crs
    assert crs.vertical == vertical_crs

    # With compound CRS
    horizontal_crs = pyproj.CRS.from_epsg(7415)
    vertical_crs = pyproj.CRS.from_epsg(7415)
    crs = CoordinateReferenceSystems(horizontal=horizontal_crs, vertical=vertical_crs)
    assert crs.horizontal == horizontal_crs
    assert crs.vertical == vertical_crs


def test_coordinate_reference_system_init_with_invalid_horizontal_CRS() -> None:
    """Test initialization of CoordinateReferenceSystems with invalid horizontal CRS."""
    # Invalid horizontal CRS: None
    with pytest.raises(TypeError, match="horizontal"):
        CoordinateReferenceSystems(horizontal=None, vertical=pyproj.CRS.from_epsg(5710))

    # Invalid horizontal CRS: Vertical CRS
    with pytest.raises(ValueError, match="horizontal"):
        CoordinateReferenceSystems(
            horizontal=pyproj.CRS.from_epsg(5710), vertical=pyproj.CRS.from_epsg(5710)
        )


def test_coordinate_reference_system_init_with_invalid_vertical_CRS() -> None:
    """Test initialization of CoordinateReferenceSystems with invalid vertical CRS."""
    # Invalid vertical CRS: None
    with pytest.raises(TypeError, match="vertical"):
        CoordinateReferenceSystems(
            horizontal=pyproj.CRS.from_epsg(28992), vertical=None
        )

    # Invalid vertical: Projected CRS
    with pytest.raises(ValueError, match="vertical"):
        CoordinateReferenceSystems(
            horizontal=pyproj.CRS.from_epsg(28992), vertical=pyproj.CRS.from_epsg(28992)
        )


def test_coordinate_reference_system_from_epsg() -> None:
    """Test constructor method `from_espg`."""
    # Valid input
    crs = CoordinateReferenceSystems.from_epsg(horizontal=28992, vertical=5710)
    assert crs.horizontal == pyproj.CRS.from_epsg(28992)
    assert crs.vertical == pyproj.CRS.from_epsg(5710)

    # Invalid horizontal EPSG code
    with pytest.raises(pyproj.exceptions.CRSError):
        CoordinateReferenceSystems.from_epsg(horizontal=99999, vertical=5710)

    # Invalid vertical EPSG code
    with pytest.raises(pyproj.exceptions.CRSError):
        CoordinateReferenceSystems.from_epsg(horizontal=28992, vertical=99999)


def test_coordinate_reference_system__eq__method() -> None:
    """Test the __eq__ method of CoordinateReferenceSystems."""
    crs_1 = CoordinateReferenceSystems.from_epsg(28992, 5709)
    crs_2 = CoordinateReferenceSystems.from_epsg(28992, 5709)
    crs_3 = CoordinateReferenceSystems.from_epsg(31370, 5710)
    crs_4 = CoordinateReferenceSystems.from_epsg(28992, 5710)
    crs_5 = CoordinateReferenceSystems.from_epsg(31370, 5709)

    assert crs_1 == crs_2
    assert crs_1 != crs_3
    assert crs_1 != crs_4
    assert crs_1 != crs_5
    assert crs_2 != crs_3
    assert crs_2 != crs_4
    assert crs_3 != crs_4
    assert crs_4 != crs_5

    assert crs_1 == crs_1
    assert crs_1 != None
    assert crs_1 != "EPSG:4326"
