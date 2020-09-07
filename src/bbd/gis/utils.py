"""
GIS utility functions.
"""

from pathlib import Path
import logging
import json

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


def extract_from_census_json(fp, headers: list) -> dict:
    """Extract column data for the requested headers"""

    with open(fp, "r") as f:
        data = json.load(f)

    # Top row is header row
    all_headers = data[0]

    # Get indexes for each requested header
    indexes = [all_headers.index(h) for h in headers]

    # Construct data container
    d = {h: [] for h in headers}

    # Pull out the requested data in each row
    for row in data[1:]:  # Skip header row

        [d[h].append(row[i]) for h, i in zip(headers, indexes)]

    return d


if __name__ == "__main__":
    x = are_coordinates_in_shape(
        [-80.09608714445338],
        [26.28538264986883],
        str(Path.cwd() / "temp_gis/high_rises/high_rises/"),
        "name",
    )

    print(x)
