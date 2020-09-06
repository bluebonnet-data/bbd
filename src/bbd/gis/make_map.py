from pathlib import Path

import shapefile
import folium


def make_map(shpf_path: str, data: dict, join_on: str, join_on_alias: str = None):
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
    """
    data = data.copy()
    joiner = data.pop(join_on)  # List of values to join shapefile and data on
    if joiner is None:
        raise KeyError(
            f"The join_on parameter '{join_on}' was not found in the data's keys: {data.keys()}"
        )

    if not all([isinstance(v, list) for v in data.values()]):
        raise ValueError("All values in the data dict must be lists")

    if not all([len(joiner) == len(v) for v in data.values()]):
        raise ValueError("All values in the data dict must be the same length!")

    # Read shapefile
    with shapefile.Reader(shpf_path) as shpf:
        geojson = shpf.__geo_interface__

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
        [properties.update({k: ""}) for k in data.keys()]

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

    # Determine tooltip fields and display values
    base_fields = list(data.keys())

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
        # style_function=style_function, # TODO add style function
        tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, localize=True),
    )
