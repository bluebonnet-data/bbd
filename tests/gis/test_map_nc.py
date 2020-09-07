from pathlib import Path
import json

import folium

from bbd import gis


data_dir = Path(__file__).parent / "shapefiles/nc/"


def test_map_nc():

    # Read race data per county subdivision
    # https://api.census.gov/data/2010/dec/sf1?get=group(H6),NAME&for=county:*&in=state:37
    with open(data_dir / "nc_race_by_county.json", "r") as f:
        jdata = json.load(f)

    # Extract relevant data (that we want to plot)
    headers = jdata[0]

    names = []
    name_index = headers.index("NAME")

    geoids = []
    geoid_index = headers.index("GEO_ID")

    # NOTE: H00600[1-8]: Race
    H006001 = []
    H006002 = []
    H006003 = []
    H006004 = []
    H006005 = []
    H006006 = []
    H006007 = []
    H006008 = []

    H006001_index = headers.index("H006001")
    H006002_index = headers.index("H006002")
    H006003_index = headers.index("H006003")
    H006004_index = headers.index("H006004")
    H006005_index = headers.index("H006005")
    H006006_index = headers.index("H006006")
    H006007_index = headers.index("H006007")
    H006008_index = headers.index("H006008")

    for row in jdata[1:]:  # Skip header row
        names.append(row[name_index])
        geoids.append(row[geoid_index][-5:])  # .shp GEOID uses last 10 digits

        H006001.append(float(row[H006001_index]))
        H006002.append(float(row[H006002_index]))
        H006003.append(float(row[H006003_index]))
        H006004.append(float(row[H006004_index]))
        H006005.append(float(row[H006005_index]))
        H006006.append(float(row[H006006_index]))
        H006007.append(float(row[H006007_index]))
        H006008.append(float(row[H006008_index]))

    data = {
        "Name": names,
        "GEOID": geoids,
        "Total": H006001,
        "White": H006002,
        "Black or African American": H006003,
        "American Indian and Alaska Native": H006004,
        "Asian": H006005,
        "Native Hawaiian and Other Pacific Islander": H006006,
        "Some Other Race": H006007,
        "Two or More Races": H006008,
        "Percent White": [w / t if not t == 0 else 1 for w, t in zip(H006002, H006001)],
    }

    # Make GIS GeoJson map object
    # Shapefile from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php
    # Search for "County,"" then select "North Carolina"
    data_map = gis.make_map(
        data_dir / "tl_2019_37_county", data, join_on="GEOID", color_by="Percent White",
    )

    # Location of one coordinate
    coordinate = list(data_map.data["features"][0]["geometry"]["coordinates"][0][0])
    coordinate.reverse()  # coordinates are stored (long, lat), need them in (lat, long)

    # Create leaflet map and add GeoJson map to it
    m = folium.Map(location=coordinate, tiles="cartodbpositron", zoom_start=7)
    data_map.add_to(m)

    # Write output file
    save_file = Path.cwd() / "user/map.html"
    save_file.parent.mkdir(exist_ok=True, parents=True)
    m.save(str(save_file))


if __name__ == "__main__":
    test_map_nc()
