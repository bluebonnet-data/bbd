from pathlib import Path

from bbd import census, gis


data_dir = Path(__file__).parent / "shapefiles/co/"


def test_map_colorado():

    # Read congresisonal district data
    # Median household income estimate is "DP03_0062E", https://api.census.gov/data/2018/acs/acs1/profile/groups/DP03.html
    # https://api.census.gov/data/2018/acs/acs1/profile?get=group(DP03),NAME&for=congressional%20district:*&in=state:08
    data = census.extract_from_json(
        data_dir / "DP03_08_cd.json", headers=["NAME", "GEO_ID", "DP03_0062E"]
    )

    # .shp GEOID uses last 4 digits
    data["GEOID"] = [geoid[-4:] for geoid in data["GEO_ID"]]

    # Create column of floats (to color by)
    data["Median Household Income"] = [float(x) for x in data["DP03_0062E"]]

    # Create column of nicely formatted strings (to display)
    data["Median Household Income (pretty format)"] = [
        "${:,.2f}".format(x) for x in data["Median Household Income"]
    ]

    aliases = {
        "NAME": "Name",
        "GEO_ID": "GEOID",
        "Median Household Income (pretty format)": "Median Household Income",
    }

    # Make and save GIS GeoJson map object
    # Shapefile from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php
    # Search for "Congressional Districts"
    gis.make_map(
        data_dir / "tl_2019_08_cd116",
        data,
        join_on="GEOID",
        color_by="Median Household Income",
        include=aliases,
        save_to=Path.cwd() / "user/map.html",
    )


def test_map_colorado_like_readme():

    # Read congresisonal district data
    # Median household income estimate is "DP03_0062E", https://api.census.gov/data/2018/acs/acs1/profile/groups/DP03.html
    # https://api.census.gov/data/2018/acs/acs1/profile?get=group(DP03),NAME&for=congressional%20district:*&in=state:08
    data = census.extract_from_json(
        data_dir / "DP03_08_cd.json", headers=["NAME", "GEO_ID", "DP03_0062E"]
    )

    # .shp GEOID uses last 4 digits
    data["GEOID"] = [geoid[-4:] for geoid in data["GEO_ID"]]

    # Create column of floats (to color by)
    data["Median Household Income"] = [float(x) for x in data["DP03_0062E"]]

    # Create column of nicely formatted strings (to display)
    data["Median Household Income (pretty format)"] = [
        "${:,.2f}".format(x) for x in data["Median Household Income"]
    ]

    # Make and save GIS GeoJson map object
    # Shapefile from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php
    # Search for "Congressional Districts"
    gis.make_map(
        data_dir / "tl_2019_08_cd116",
        data,
        join_on="GEOID",
        color_by="Median Household Income",
        save_to=Path.cwd() / "user/map.html",
    )


if __name__ == "__main__":
    test_map_colorado_like_readme()
