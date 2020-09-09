from pathlib import Path
from typing import Union

import shapefile
import folium
import branca

from .utils import get_geojson_bounds


def make_map(
    shpf_path: str,
    data: dict,
    join_on: str,
    color_by: str = None,
    include: Union[list, dict, None] = None,
    map_: folium.Map = None,
    save_to: Union[str, Path, None] = None,
):
    """Creates a folium.features.GeoJson map object.
    Joins map properties with the properties in `data` and shows `data` in the map popup tooltips.

    :param shpf_path: File path to shapefile. No need to include file extension.
    :param data: dict in the form of {join_on: [values], "other property": [values]}.
        If you want the tooltip properties to be displayed in any particular order,
        you can use an `OrderedDict`.
    :param join_on: The data key (header) used to join the shapefile property table with `data`.
        This parameter must be a key in the `data` dict.
    :param color_by: Optional. If None (default) all shapes will be the same color. Otherwise, a linear
        colormap will be generated based on the min and max values of the data[color_by] list.
    :param include: Optional. If None (default) all keys in the `data` table will be shown in the
        tooltip. If `include` is a `list` of `str`, only those values will be shown in the tooltip.
        If `include` is a `dict` of `{str:str}`, the tooltip fields are set to the 'keys' and the
        aliases are set to the 'values'.
    :param map_: Optional. If included, the folium.GeoJson and branca.ColorMap objects will be added to
        the map as they are created. If not included, you can add the folium.GeoJson object manually.
    :param save_to: Optional path to save file. If included, the map will be automatically saved to
        the location specified by `save_to`. If you use this parameter, you don't need to pass in a `map_`
        as one will automatically generated with default settings.
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

    # If the caller wants us to save but does not provide a map, create one
    if save_to is not None and map_ is None:
        map_ = folium.Map(tiles="cartodbpositron")

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
            caption=str(color_by),
        )

        if map_ is not None:
            map_.add_child(colormap)

        def style_function(feature: dict):
            value = feature["properties"][color_by]
            fill = colormap(value) if value is not None else "grey"
            return {
                "fillColor": fill,
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.5,
            }

    if isinstance(include, list):  # Display these fields as is
        fields = include
        aliases = include

    elif isinstance(include, dict):  # Display fields as key=field, value=alias
        fields = []
        aliases = []
        [(fields.append(k), aliases.append(v)) for k, v in include.items()]

    elif include is None:  # Display all fields as given in the joined data
        fields = list(data.keys())
        aliases = fields

    else:
        raise ValueError(
            f"The `include` parameter must be a list, dict, or None. Not: {type(include)}"
        )

    # Create GeoJson map object
    geojson_map = folium.GeoJson(
        geojson,
        name=Path(shpf_path).name,
        style_function=style_function if color_by else None,
        tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, localize=True),
    )

    # Add to folium.Map if that parameter was passed in
    if map_ is not None:
        geojson_map.add_to(map_)

    # Save map_ if a save path was provided
    if save_to is not None:
        assert map_ is not None

        # Fit bounds to the GeoJson shapes
        map_.fit_bounds(get_geojson_bounds(geojson_map.data))

        # Ensure path exists
        Path(save_to).parent.mkdir(exist_ok=True, parents=True)

        # Save
        map_.save(str(save_to))

    return geojson_map
