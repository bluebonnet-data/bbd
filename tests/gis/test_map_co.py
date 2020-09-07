from pathlib import Path
import json
import locale

import folium

from bbd import gis


locale.setlocale(locale.LC_ALL, "en_CA.UTF-8")
data_dir = Path(__file__).parent / "shapefiles/co/"


def test_map_colorado():

    # Read congresisonal district data
    with open(data_dir / "DP03_08_cd.json", "r") as f:
        jdata = json.load(f)

    # Extract relevant data (that we want to plot)
    headers = jdata[0]

    names = []
    name_index = headers.index("NAME")

    geoids = []
    geoid_index = headers.index("GEO_ID")

    # NOTE: DP03_0062E: Median household income estimate, https://api.census.gov/data/2018/acs/acs1/profile/groups/DP03.html
    DP03_0062E_currency = []
    DP03_0062E_value = []
    DP03_0062E_index = headers.index("DP03_0062E")

    for row in jdata[1:]:  # Skip header row
        names.append(row[name_index])
        geoids.append(row[geoid_index][-4:])  # Shapefile GEOID only uses last 4 digits

        DP03_0062E_float = float(row[DP03_0062E_index])
        DP03_0062E_value.append(DP03_0062E_float)
        DP03_0062E_currency.append(locale.currency(DP03_0062E_float, grouping=True))

    data = {
        "Name": names,
        "CD116FP": geoids,  # Shapefile GEOIDs are stored under this property idk why
        "Median Household Income": DP03_0062E_currency,
        "Median Household Income value": DP03_0062E_value,
    }

    # Make GIS GeoJson map object
    data_map = gis.make_map(
        data_dir / "tl_2019_08_cd116",
        data,
        join_on="CD116FP",
        color_by="Median Household Income value",
        exclude=["Median Household Income value"],  # Only needed to color by
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
    test_map_colorado()
