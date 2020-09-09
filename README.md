# BBD: Bluebonnet Data Library

**BBD** is a library for helping teams perform political campaign data analysis.

![tests](https://github.com/bluebonnet-data/bbd/workflows/tests/badge.svg)

## Installing BBD

BBD is available on PyPI:

```console
python -m pip install bbd
```

## Example

### Getting Census Data
First, find the data you want to visualize. This is often easiest through the census API, and the next bit of text will read a bit like a "How to Get Census Data" tutorial. In the future there are plans to automate this process through the **bbd** library.

For our working example, we'll use median household income (which is coded in the census data as as "DP03_0062E").

We can simply downloaded the json data from [here](https://api.census.gov/data/2018/acs/acs1/profile?get=group(DP03),NAME&for=congressional%20district:*&in=state:08) and save it to "C:/DP03_08_cd.json" (or wherever).

    https://api.census.gov/data/2018/acs/acs1/profile?get=group(DP03),NAME&for=congressional%20district:*&in=state:08

For more information on how to come up with your own census API requests I'd highly recommend the first 6 minutes of [this video](https://www.census.gov/library/video/2020/using-api-all-results-for-acs-table.html). For reference, the following table describes the basic elements of the API call used to get this working example's data.

| URL Part               | Meaning
| ----------------       |-------------
| get=group(DP03)        | Data columns include those in group DP03 (economics)
| ,NAME                  | Include name of each entity, just a nicety
| for=congr...district:* | One row for each congressional district
| in=state:08            | Only get rows for state 08 (Colorado)

This census data is stored more or less as a big table in json format:

```json
[
    ["NAME", "GEO_ID", "DP03_0001E", ...] // Headers
    ["Congressional District 4", "5001600US0801", "693303", ...] // Data
    ["...", "...", "...", ...] // Data
]
```

We'll need to transform it into a format that is plottable. To do so, the `gis.extract_from_census_json` method should do the trick!

```python
>>> from bbd import gis
>>> data = gis.extract_from_census_json(data_file, headers=["NAME", "GEO_ID", "DP03_0062E"])
>>> 
```

# TODO
Get feedback and see whether or not to finish this README!

```python
>>> # Misc notes...
>>>
>>> # First, find the data you want to visualize.
>>> # This is often easiest through the census API.
>>> # In this example, we'll use median household income (coded as "DP03_0062E")
>>>
>>> # (Manually) download the json data from the following link:
>>> # https://api.census.gov/data/2018/acs/acs1/profile?get=group(DP03),NAME&for=congressional%20district:*&in=state:08
>>>
>>> # To find your own data, this video is a good place to start:
>>> # https://www.census.gov/library/video/2020/using-api-all-results-for-acs-table.html
>>>
>>> # Let's say that the data is stored at "C:/DP03_08_cd.json"
>>> # You could also `get` the http response with the requests package if you prefer!
>>> census_json_path = "C:/DP03_08_cd.json"
>>>
>>> # Now
>>> data = gis.extract_from_census_json(
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

    # Initialize leaflet map
    map_ = folium.Map(tiles="cartodbpositron")

    # Make GIS GeoJson map object
    # Shapefile from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php
    # Search for "Congressional Districts"
    geojson_map = gis.make_map(
        data_dir / "tl_2019_08_cd116",
        data,
        join_on="GEOID",
        color_by="Median Household Income",
        include=aliases,
        map_=map_,
    )

    # Set map location to the first coordinate in the GeoJson
    map_.fit_bounds(gis.get_geojson_bounds(geojson_map.data))

    # Write output file
    save_file = Path.cwd() / "user/map.html"
    save_file.parent.mkdir(exist_ok=True, parents=True)
    map_.save(str(save_file))
```

---
Developed by [Bluebonnet Data](https://www.bluebonnetdata.org/)