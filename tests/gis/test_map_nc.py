from pathlib import Path

from bbd import census, gis


data_dir = Path(__file__).parent / "shapefiles/nc/"


def test_map_nc():

    # Read race data per county subdivision
    # https://api.census.gov/data/2010/dec/sf1?get=group(H6),NAME&for=county:*&in=state:37
    data = census.load_json_file(
        data_dir / "nc_race_by_county.json",
        headers=[
            "NAME",
            "GEO_ID",
            "H006001",
            "H006002",
            "H006003",
            "H006004",
            "H006005",
            "H006006",
            "H006007",
            "H006008",
        ],
    )

    # .shp GEOID uses last 5 digits
    data["GEOID"] = [geoid[-5:] for geoid in data["GEO_ID"]]

    # Percentage of white people out of the total respondants (to color by)
    data["% White"] = [
        float(w) / float(t) if not t == 0 else 100
        for w, t in zip(data["H006002"], data["H006001"])
    ]

    # Percentage of white people (formatted nicely for display)
    data["% White (pretty format)"] = [f"{round(x * 100, 1)}%" for x in data["% White"]]

    aliases = {
        "NAME": "Name",
        "GEO_ID": "GEOID",
        "H006001": "Total",
        "H006002": "White",
        "H006003": "Black",
        "H006004": "Native American",
        "H006005": "Asian",
        "H006006": "Pasific Islander",
        "H006007": "Other",
        "H006008": "Two or More",
        "% White (pretty format)": "Percent White",
    }

    # Make and save GIS GeoJson map object
    # Shapefile from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php
    # Search for "County,"" then select "North Carolina"
    gis.make_map(
        data_dir / "tl_2019_37_county",
        data,
        join_on="GEOID",
        color_by="% White",
        include=aliases,
        save_to=Path.cwd() / "user/map.html",
    )


if __name__ == "__main__":
    test_map_nc()
