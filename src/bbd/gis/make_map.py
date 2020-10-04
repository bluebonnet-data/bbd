from pathlib import Path
from typing import Optional, Union

import shapefile
import folium
import branca

from ..working_directory import working_directory

from .magic import Magic
from .utils import get_geojson_bounds, resolve_shapefile_path
from .trim_shapefile import trim_shapefile


def make_map(
    shapefile_path: Union[Path, str],
    data: dict,
    join_on: str,
    color_by: Optional[str] = None,
    include: Optional[Union[list, dict]] = None,
    map_: Optional[folium.Map] = None,
    save_to: Optional[Union[str, Path]] = None,
    trim: Optional[bool] = False,
):
    """Creates a folium.features.GeoJson map object.
    Joins map properties with the properties in `data` and shows `data` in the map popup tooltips.

    :param shapefile_path: File path to shapefile. No need to include file extension.
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

    # Allow shapefile path to be relative to working directory
    shapefile_path = working_directory.resolve(shapefile_path)

    # If the shapefile path is a directory with a .shp file of the same name,
    # that's okay. It is also okay to just pass in the path to the file directly.
    shapefile_path = resolve_shapefile_path(shapefile_path)

    # Trim the shapefile if requested
    if trim is True:
        shapefile_path = trim_shapefile(shapefile_path, join_on, joiner)

    # Read shapefile
    with shapefile.Reader(str(shapefile_path)) as shpf:
        # NOTE: This is a work-around until the shapefile.Reader.__geo_interface__
        # bug is fixed... TODO add bug report number
        geojson = {
            "type": "FeatureCollection",
            "bbox": shpf.bbox,
            "features": [sfr.__geo_interface__ for sfr in shpf.iterShapeRecords()],
        }

    # Presently, can only operate on feature collections
    if not geojson["type"] == "FeatureCollection":
        raise AssertionError(
            f"Shapefile {shapefile_path} must be a FeatureCollection, not '{geojson['type']}''"
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

        # Remove magic numbers that represent missing data
        color_by_values = [x for x in data[color_by] if x not in Magic.MISSING_VALUES]

        colormap = branca.colormap.LinearColormap(
            colors=["#764aed", "#fc6665"],
            index=None,  # Will default to linear range between colors
            vmin=min(color_by_values),
            vmax=max(color_by_values),
            caption=str(color_by),
        )

        if map_ is not None:
            map_.add_child(colormap)

        def style_function(feature: dict):
            value = feature["properties"][color_by]

            # Don't color missing values and don't color if
            # the shape doesn't have the property to color by.
            if value in Magic.MISSING_VALUES or value is None:
                fill = "grey"
            else:
                fill = colormap(value)

            return {
                "fillColor": fill,
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.5,
            }

    else:
        style_function = None

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
        name=shapefile_path.name,
        style_function=style_function,
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

        # Allow save_to to be relative to working directory
        save_to = working_directory.resolve(save_to)

        # Ensure path exists
        Path(save_to).parent.mkdir(exist_ok=True, parents=True)

        # Save
        map_.save(str(save_to))

    return geojson_map
