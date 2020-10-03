from pathlib import Path
from bbd import census, gis, working_directory


here = Path(__file__).parent
working_directory.path = here / "data"

api_key_file = here.parent / "user/census_api_key.txt"
with open(api_key_file, "r") as f:
    census.api_key.key = f.readlines()[0]

# Say you were interested in median household income in colorado, per census tract.
# A good place to start looking for that data is on the census data set website:
# https://www.census.gov/data/developers/data-sets.html
#
# I selected American Community Survey 5-Year data, and took a look at the "Data Profiles"
# that were available. We can see that income is coded as "DP03_0062E":
# https://api.census.gov/data/2018/acs/acs5/profile/variables.html
#
# For reference, you can use the following census API call to get that data.
# https://api.census.gov/data/2018/acs/acs5/profile?get=NAME,DP03_0062E&for=tract:*&in=state:08&in=county:*
#
# We can retreive that data with the following call
data = census.get_acs(
    geography=census.Geography.TRACT,
    variables=["NAME", "DP03_0062E"],
    year=2018,
    dataset=census.DataSets.ACS5_PROFILE,
    state="co",
    county="069",  # Larimer County
    cache=True,
)

# Since we want to show data in colorado, per census tract, we can get that from this site:
# https://www.census.gov/cgi-bin/geo/shapefiles/index.php
#
# We can also retreive it automatically with the following call
shapefile_path = census.get_shapefile(
    geography=census.Geography.TRACT,
    state="co",
    year=2019,
    cache=True,
)

# The shapefile GEOID is coded with 11 digits (STATE:2 + COUNTY:3 + TRACT:6 = GEOID:11)
# More detail here: # https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html
#
# To make it possible to join the census data with the shapefile, we need to make
# a column that matches between the census data and the shapefile properties. For this
# example, we can simply combine the census data state, county, and tract
data["GEOID"] = [
    s + c + t for s, c, t in zip(data["state"], data["county"], data["tract"])
]

# Right now the median household income is stored as a string (e.g. "11456.84"). This
# is great for viewing, but makes it hard to do any numerical calculations with.
# Here we will create column of "Median Household Income" but as a float (a number,
# e.g. 11456.84). This will be used to generate the colormap.
data["Median Household Income"] = [float(x) for x in data["DP03_0062E"]]

# Just to make the map prettier, it would be nice to format the median household
# income with a "$" and commas between every third number (e.g. "$11,456.84").
# This will be shown in the map's tooltip.
data["Median Household Income (pretty format)"] = [
    "${:,.2f}".format(x) for x in data["Median Household Income"]
]

# Make and save GIS GeoJson map object of "Congressional Districts"
# Shapefile from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php
gis.make_map(
    shapefile_path,
    data,
    join_on="GEOID",
    color_by="Median Household Income",
    save_to=here / "co-map.html",
)
