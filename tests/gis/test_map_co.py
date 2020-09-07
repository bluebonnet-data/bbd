from pathlib import Path

import folium

from bbd import gis


data_dir = Path(__file__).parent / "shapefiles/co/"


def test_map_colorado():

    # Read congresisonal district data
    # Median household income estimate is "DP03_0062E", https://api.census.gov/data/2018/acs/acs1/profile/groups/DP03.html
    data = gis.extract_from_census_json(
        data_dir / "DP03_08_cd.json", headers=["NAME", "GEO_ID", "DP03_0062E"]
    )

    # .shp GEOID uses last 4 digits
    data["GEOID"] = [geoid[-4:] for geoid in data["GEO_ID"]]

    # Create column of floats (to color by)
    data["Income Value"] = [float(x) for x in data["DP03_0062E"]]

    # Create column of nicely formatted strings (to display)
    data["Median Household Income"] = [
        "${:,.2f}".format(x) for x in data["Income Value"]
    ]

    aliases = {
        "NAME": "Name",
        "GEO_ID": "GEOID",
        "Median Household Income": "Median Household Income",
    }

    # Make GIS GeoJson map object
    data_map = gis.make_map(
        data_dir / "tl_2019_08_cd116",
        data,
        join_on="GEOID",
        color_by="Income Value",
        include=aliases,
    )

    # Location of one coordinate
    coordinate = gis.get_first_coordinate(data_map.data)

    # Create leaflet map and add GeoJson map to it
    m = folium.Map(location=coordinate, tiles="cartodbpositron", zoom_start=7)
    data_map.add_to(m)

    # Write output file
    save_file = Path.cwd() / "user/map.html"
    save_file.parent.mkdir(exist_ok=True, parents=True)
    m.save(str(save_file))


if __name__ == "__main__":
    test_map_colorado()
