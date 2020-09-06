import tempfile

import shapefile

import bbd.gis as gis


def test_utils():

    path = tempfile.mktemp(suffix="")  # no extension

    with shapefile.Writer(path) as w:
        w.shapeType = shapefile.POLYGON
        w.field("test_name", "C")  # text field

        w.poly([[[0, 0], [0, 100], [100, 100], [100, 0]]])  # poly 1, a square
        w.record("poly1")

    xCoords = [-10, 10, 50, 100]

    yCoords = [-10, 10, 100, 100]

    withinShape = gis.are_coordinates_in_shape(xCoords, yCoords, path, "test_name")

    assert withinShape[0] is None  # Outside shape
    assert withinShape[1] == "poly1"  # Inside shape
    assert withinShape[2] == "poly1"  # On shape boundary
    assert withinShape[3] == "poly1"  # On shape vertex
