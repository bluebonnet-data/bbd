from pathlib import Path

import shapefile
import folium
import branca


def make_map(
    shpf_path: str,
    data: dict,
    join_on: str,
    join_on_alias: str = None,
    color_by: str = None,
    extend_include: list = [],
    exclude: list = [],
):
    """Creates a folium.features.GeoJson map object.
    Joins map properties with the properties in `data` and shows `data` in the map popup tooltips.

    :param shpf_path: File path to shapefile. No need to include file extension.
    :param data: dict in the form of {join_on: [values], "other property": [values]}.
        If you want the tooltip properties to be displayed in any particular order,
        you can use an `OrderedDict`.
    :param join_on: The data key (header) used to join the shapefile property table with `data`.
        This parameter must be a key in the `data` dict.
    :param join_on_alias: If None (default) the `join_on` property will not be shown in the tooltip.
        If a value is given, the `join_on` parameter will be shown with the `join_on_alias` name
        at the top of the tooltip.
    :param color_by: If None (default) all shapes will be the same color. Otherwise, a linear
        colormap will be generated based on the min and max values of the data[color_by] list.
    """

    data = data.copy()

    try:
        joiner = data.pop(join_on)  # List of values to join shapefile and data on
    except KeyError:
        raise KeyError(
            f"The join_on parameter '{join_on}' was not found in the data's keys: {data.keys()}"
        )

    if not all([isinstance(v, list) for v in data.values()]):
        raise ValueError("All values in the data dict must be lists")

    if not all([len(joiner) == len(v) for v in data.values()]):
        raise ValueError("All values in the data dict must be the same length!")

    # Read shapefile
    with shapefile.Reader(str(shpf_path)) as shpf:
        # NOTE: This is a work-around until the shapefile.Reader.__geo_interface__
        # bug is fixed... TODO add bug report number
        features = [f.__geo_interface__ for f in shpf.iterShapeRecords()]
        geojson = {"type": "FeatureCollection", "bbox": shpf.bbox, "features": features}

    # Presently, can only operate on feature collections
    if not geojson["type"] == "FeatureCollection":
        raise AssertionError(
            f"Shapefile {shpf_path} must be a FeatureCollection, not '{geojson['type']}''"
        )

    # Add new data properties to geojson features
    for feature in geojson["features"]:

        properties = feature["properties"]

        # Initialize empty property fields. All features must have
        # the same properties.
        [properties.update({k: None}) for k in data.keys()]

        # Check if this feature has the property to join on
        try:
            key_property = properties[join_on]
        except KeyError:
            continue

        # Get the index of this feature's property in the data
        # that we are about to insert.
        try:
            join_index = joiner.index(key_property)
        except ValueError:
            continue

        # Add new property data to the feature
        [properties.update({k: data[k][join_index]}) for k in data.keys()]

    # The bbox is stored as a shapefile._Array, which is not serializable
    geojson["bbox"] = list(geojson["bbox"])

    # Create style function
    if color_by is not None:
        colormap = branca.colormap.LinearColormap(
            colors=["#764aed", "#fc6665"],
            index=None,  # Will default to linear range between colors
            vmin=min(data[color_by]),
            vmax=max(data[color_by]),
            caption=f"{color_by} Density",
        )

        def style_function(feature: dict):
            value = feature["properties"][color_by]
            fill = colormap(value) if value is not None else "grey"
            return {
                "fillColor": fill,
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.5,
            }

    # Determine tooltip fields and display values
    base_fields = list(data.keys())

    base_fields.extend(extend_include)  # Extend field list with custom input
    [base_fields.remove(x) for x in exclude if x in base_fields]  # Remove requested

    if join_on_alias is None:
        fields = base_fields
        aliases = fields
    else:
        fields = [join_on] + base_fields
        aliases = [join_on_alias] + base_fields

    # Create GeoJson map object
    return folium.GeoJson(
        geojson,
        name=Path(shpf_path).name,
        style_function=style_function if color_by else None,
        tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, localize=True),
    )
