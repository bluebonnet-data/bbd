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

from bbd import census, gis, working_directory


# Set the working directory (where files get stored)
here = Path(__file__).parent.absolute()
working_directory.path = here / "data"

# Save api key as the first line of a `census_api_key.txt` file in this directory
api_key_file = here / "census_api_key.txt"
with open(api_key_file, "r") as f:
    census.api_key.key = f.readlines()[0]

# In Texas, looking at 2018 ACS block groups.
shapefile_dir = census.get_shapefile(
    geography=census.Geography.BLOCKGROUP,
    state="tx",
    year=2018,
    cache=True,
)

# Extract and reformat census data
data = census.get_acs(
    geography=census.Geography.BLOCKGROUP,
    variables=["NAME", "B03003_001E", "B03003_002E", "B03003_003E"],
    year=2018,
    dataset=census.DataSets.ACS5_DETAIL,
    state="tx",
    county="201",  # Harris County
    cache=True,
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
    shapefile_dir,
    data,
    join_on="GEOID",
    color_by="% Hispanic or Latino Origin",
    include=aliases,
    save_to=here / "tx-map.html",
    trim=True,
)
