"""
GIS utility functions.
"""

from pathlib import Path
import logging

import shapefile
from shapely.geometry import Point
from shapely.geometry import Polygon


def are_coordinates_in_shape(
    latitudes: list, longitudes: list, shapefile_path: str, record_key: str
):
    """
    Takes the latitudes and longitudes as lists of equal length and
    determines whether or not they are within a given shapefile at path `shapefile_path`.

    Returns a list containing the record identifiers
    (retreived with from each shapefile record as record(i)[record_key])
    of the polygon containing the point, or None if no polygons contain the point.
    """

    if not len(latitudes) == len(longitudes):
        raise ValueError("Latitudes and longitudes must be the same length!")

    # Generate coordinate points
    points = [Point(lat, lon) for lat, lon in zip(latitudes, longitudes)]

    # Initialize default list of polygon ids that correspond to each point
    polygonIds = [None for _ in latitudes]

    # Read shapefile
    with shapefile.Reader(shapefile_path) as shpf:

        logging.info(f"Reading shapefile: {shapefile_path}")

        if shpf.shapeType not in (
            shapefile.POLYGON,
            shapefile.POLYGONM,
            shapefile.POLYGONZ,
        ):
            raise ValueError(
                "Cannot determing bounding polygons of shapefiles that do not have a polygon shape type."
            )

        # Enumerate over each each polygon
        num_polygons = len(shpf)
        for n, shape_record in enumerate(shpf.iterShapeRecords()):

            logging.info(f"Checking shape {n + 1}/{num_polygons}")

            # Attempt to get record value
            try:
                record_value = shape_record.record[record_key]
            except KeyError:
                raise KeyError(
                    f"Requested key {record_key} was not found in shape {shape_record} "
                    f"in the file: {shapefile_path}. The ShapeRecord's fields are: {shape_record.fields}"
                )

            # Iterate over each group of geometry points
            # (multiple groups in the case of a multi-polygon)
            #
            # Note that the parts list constains the beginning
            # indices of each collection of points.
            shape = shape_record.shape
            for i in range(len(shape.parts)):

                i_start = shape.parts[i]  # Index of the first point

                if i == len(shape.parts) - 1:  # This is the last part
                    i_end = len(shape.points)  # End index is back of list
                else:  # Not the last part
                    i_end = shape.parts[i + 1]  # End before next collection

                # Get bounding polygon from source coordinate points
                polygon = Polygon(shape.points[i_start:i_end])

                # Record Id if the point is in this polygon
                # If Id has already been recorded, keep it
                polygonIds = [
                    record_value if id is None and p.intersects(polygon) else id
                    for p, id in zip(points, polygonIds)
                ]

    return polygonIds


def get_geojson_bounds(geojson: dict):
    """Returns geojson bounds in format compatible with
    folium.Map.set_bounds() method.

    Returns two (lat, long) points: [southwest, northeast]
    """

    # NOTE: bbox is given as:
    #   2D: [SW lat, SW long, NE lat, NE long]
    #   3D: [SW lat, SW long, SW elev, NE lat, NE long, NE elev]
    bbox = geojson["bbox"]

    # Not sure if this is a PyShp BUG, but it seems like the coordinates
    # are consistently stored (long, lat) instead of (lat, long)
    if len(bbox) == 4:  # 2D GeoJson
        return [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]
    elif len(bbox) == 6:  # 3D GeoJson
        return [[bbox[1], bbox[0]], [bbox[4], bbox[3]]]
    else:
        raise NotImplementedError(
            f"Sorry! Expected bbox with 4 or 6 elements. Got: {bbox}"
        )


def resolve_shapefile_path(in_path) -> Path:
    """Resolves to a shapefile path.

    If in_path is a directory that contains a child with the same name and a '.shp'
    extension, this method will return a path to that shapefile. Otherwise, the
    'in_path' is returned.

    This is useful because often shapefiles come in zip files (in particular from
    the census ftp site), and thus the actual shapefile is nested within a folder
    of the same name.

    Example:

        Getting census shapefile with `census.get_shapefile` will result in a
        directory structure like so:
            ./tl_2018_08_tract/tl_2018_08_tract.shp

        However, we often only pass around a path to the parent directory:
            ./tl_2018_08_tract/

        Calling `resolve_shapefile_path` on this directory will resolve to the
        complete shapefile path.
            ./tl_2018_08_tract/tl_2018_08_tract.shp
    """
    p = Path(in_path)
    if p.is_dir() and (p / (p.name + ".shp")).exists():
        path_to_use = p / p.name
    else:
        path_to_use = p
    return path_to_use


if __name__ == "__main__":
    x = are_coordinates_in_shape(
        [-80.09608714445338],
        [26.28538264986883],
        str(Path.cwd() / "temp_gis/high_rises/high_rises/"),
        "name",
    )

    print(x)
