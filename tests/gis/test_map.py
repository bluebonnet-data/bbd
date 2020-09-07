from pathlib import Path
import tempfile

import folium
import pytest

from bbd import gis

m = folium.Map(
    location=[26.1920, -80.0964],  # Laud. by the Sea
    tiles="cartodbpositron",
    zoom_start=12,
)

standard_data = {
    "name": ["Bay Colony, Port Royale", "NE 48th", "08001"],
    "Demographic 1": ["bay col dem1", "NE 48th dem1", "08001 dem1"],
    "Demographic 2": ["bay col dem2", "NE 48th dem2", "08001 dem2"],
}

shapefile_path = str(Path(__file__).parent / "shapefiles/fl_high_rises/fl_high_rises")
save_path = tempfile.mktemp(suffix=".html")


def test_make_map_joins_properly():
    data = standard_data

    data_map = gis.make_map(shapefile_path, data, join_on="name", join_on_alias="Name",)

    geojson = data_map.data
    assert geojson["type"] == "FeatureCollection"

    features = geojson["features"]
    assert len(features) == 36

    feature0_props = features[0]["properties"]
    assert feature0_props["name"] == "Bay Colony, Port Royale"
    assert feature0_props["Demographic 1"] == "bay col dem1"
    assert feature0_props["Demographic 2"] == "bay col dem2"

    feature1_props = features[1]["properties"]
    assert feature1_props["name"] == "NE 48th"
    assert feature1_props["Demographic 1"] == "NE 48th dem1"
    assert feature1_props["Demographic 2"] == "NE 48th dem2"

    feature2_props = features[2]["properties"]
    assert feature2_props["name"] == "Linden Pointe Apartments"
    assert feature2_props["Demographic 1"] is None
    assert feature2_props["Demographic 2"] is None

    data_map.add_to(m)

    m.save(save_path)


def test_make_map_exception_for_bad_join_key():
    data = standard_data

    with pytest.raises(KeyError):
        gis.make_map(shapefile_path, data, join_on="Name")  # note caps


def test_make_map_exception_for_mismatched_data_size():
    data = standard_data.copy()
    data["name"] = data["name"] + ["extra element"]

    with pytest.raises(ValueError):
        gis.make_map(shapefile_path, data, join_on="name")


def test_make_map_exception_for_value_not_list():
    data = standard_data.copy()
    data["Demographic 1"] = "I am not a list"

    with pytest.raises(ValueError):
        gis.make_map(shapefile_path, data, join_on="name")


def test_make_map_tooltip_without_alias():
    data = standard_data

    data_map = gis.make_map(shapefile_path, data, join_on="name")

    children = data_map._children
    tooltip = children.popitem(last=False)[1]  # Get first tooltip

    assert tooltip.fields == ["Demographic 1", "Demographic 2"]
    assert tooltip.aliases == ["Demographic 1", "Demographic 2"]


def test_make_map_tooltip_with_alias():
    data = standard_data

    data_map = gis.make_map(shapefile_path, data, join_on="name", join_on_alias="Name")

    children = data_map._children
    tooltip = children.popitem(last=False)[1]  # Get first tooltip

    assert tooltip.fields == ["name", "Demographic 1", "Demographic 2"]
    assert tooltip.aliases == ["Name", "Demographic 1", "Demographic 2"]
