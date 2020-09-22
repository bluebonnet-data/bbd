# ACS variables
# B03003_001 -- total people who answered
# B03003_002 -- total not hispanic or latino
# B03003_003 -- total hispanic or latino
#
# API call
# https://api.census.gov/data/2018/acs/acs5?get=NAME,B03003_001E,B03003_002E,B03003_003E&for=block%20group:*&in=state:48%20county:201
#
# See variable definition here
# https://api.census.gov/data/2018/acs/acs5/variables.html

from pathlib import Path

from bbd import cache, census, gis


# Data will be downloaded to the folder this file currently resides in
here = Path(__file__).parent
cache.set_working_directory(here / "data")

# In Texas, looking at 2018 ACS block groups.
state = "tx"
year = 2018

# Download shapefiles, retreive path
shapefile_dir = census.get_shapefile(
    census.Geography.BLOCKGROUP, state, year, cache=True
)

# Extract and reformat census data
data = census.extract_from_json(
    here / "data/tx_harris_blockgroup_ethnic_origin.json",
    headers=[
        "NAME",
        "B03003_001E",
        "B03003_002E",
        "B03003_003E",
        "state",
        "county",
        "tract",
        "block group",
    ],
)

# The shapefile GEOID is coded with 11 digits (STATE:2 + COUNTY:3 + TRACT:6 + BLOCK_GROUP:1 = GEOID:12)
# More detail here: # https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html
#
# To make it possible to join the census data with the shapefile, we need to make
# a column that matches between the census data and the shapefile properties. For this
# example, we can simply combine the census data state, county, and tract
data["GEOID"] = [
    s + c + t + bg
    for s, c, t, bg in zip(
        data["state"], data["county"], data["tract"], data["block group"]
    )
]

# The shapefile comes in with the entire state of texas. We want to only show the areas
# that we have data for, i.e. we should remove all shapes that we don't have a GEOID for.
trimmed_shapefile = gis.trim_shapefile(
    in_path=shapefile_dir, join_on="GEOID", include=data["GEOID"]
)

# Percentage of hispanic or latino origin people out of the total respondants (to color by)
data["% Hispanic or Latino Origin"] = [
    float(his) / float(tot) * 100 if not tot == 0 else None
    for tot, his in zip(data["B03003_001E"], data["B03003_003E"])
]

# Formatted nicely for display
data["pretty format"] = [f"{round(x, 1)}%" for x in data["% Hispanic or Latino Origin"]]

# What to include
aliases = {
    "NAME": "Name",
    "GEOID": "GEOID",
    "B03003_001E": "Total",
    "B03003_003E": "Hispanic or Latino Origin",
    "B03003_002E": "Not Hispanic or Latino Origin",
    "pretty format": "% Hispanic or Latino Origin",
}

# Make the map!
gis.make_map(
    trimmed_shapefile,
    data,
    join_on="GEOID",
    color_by="% Hispanic or Latino Origin",
    include=aliases,
    save_to=here / "tx-map.html",
)
