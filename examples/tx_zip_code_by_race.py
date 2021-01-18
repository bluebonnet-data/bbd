"""Instructions for use

1) Make sure python is installed

2) Install the bluebonnet data package by running this command in your terminal:
    pip install bbd

3) Run this python file with the following command:
   (from your terminal in the same folder as this file):
    python tx_zip_code_by_race.py

4) Wait patiently... the first time this runs it has to download about 800 Mb of
us zip code shapefiles :/ but don't worry -- it caches them, so the next time it will
run much much faster.

5) Ta da, there should be a few exported data files.
    - data_for_team.csv -- the data you requested, can copy and paste into a spreadsheet
    - tx-zcta-map-B02001_00?E.html -- map of each demographic percentage. Open in web browser.
"""

import re
from pathlib import Path

from bbd import census, gis, working_directory


# Set the working directory (where files get stored)
here = Path(__file__).parent.absolute()
working_directory.path = here / "data"

# Save api key as the first line of a `census_api_key.txt` file in this directory
api_key_file = here / "census_api_key.txt"
with open(api_key_file, "r") as f:
    census.api_key.key = f.readlines()[0]

# ACS variables
#
# See variable definition here
# https://api.census.gov/data/2018/acs/acs5/variables.html
variables = {
    "NAME": "Name",
    "B02001_001E": "Race, total",
    "B02001_002E": "Race, white",
    "B02001_003E": "Race, black or african american",
    "B02001_004E": "Race, american indian or alaska native",
    "B02001_005E": "Race, asian",
    "B02001_006E": "Race, native hawaiian or pacific islander",
    "B02001_007E": "Race, other",
    "B02001_008E": "Race, two or more",
    "B02001_009E": "Race, two or more, excluding 'other'",
}

# Extract and reformat census data
print("getting census data")
data = census.get_acs(
    geography=census.Geography.ZCTA,
    variables=list(variables.keys()),
    year=2018,
    dataset=census.DataSets.ACS5_DETAIL,
    # state="tx",
    # county="201": "Harris County
    cache=True,
)

# Get the shapefile
print("getting shapefile (takes a long time on the first run)")
shapefile_dir = census.get_shapefile(
    geography=census.Geography.ZCTA,
    state="tx",
    year=2018,
    cache=True,
)

# We only want specific zctas
# In the future the bbd library should be able to handle this internally
# Otherwise it might be worth just biting the bullet and using numpy
print("writing output data")
with open(here / "tx_harris_county_zctas.txt", "r") as f:
    valid_zctas = [line.rstrip() for line in f.readlines()]

valid_zctas_indexes = [i for i, name in enumerate(data["NAME"]) if name in valid_zctas]

valid_data = {}
for variable, value_list in data.items():
    valid_data[variable] = [value_list[i] for i in valid_zctas_indexes]

# Print out the race data for the valid zip codes in a nicely formatted way
# that can be copied directly to excel
with open(here / "data_for_team.csv", "w") as f:
    for header in valid_data.keys():
        f.write(f"{header}\t")
    f.write("\n")
    for i in range(len(valid_data["NAME"])):
        [f.write(f"{valid_data[key][i]}\t") for key in valid_data.keys()]
        f.write("\n")

# Make entry with just the proper zcta name to play nicely with the shapefile
valid_data["ZCTA5CE10"] = valid_data["zip code tabulation area"]

# Determine percentage for all demographics
percentage_labels = []
for census_code, description in variables.items():

    if not re.match(r"B02001_00[2-9]E", census_code):
        continue

    label = f"% {description}"

    valid_data[label] = [
        float(race) / float(tot) * 100 if not tot == "0" else None
        for tot, race in zip(valid_data["B02001_001E"], valid_data[census_code])
    ]
    percentage_labels.append(label)

# Log the percentage label so it shows up nicely in the tooltip
variables.update({label: label for label in percentage_labels})

# Make all the maps!
for census_code, description in variables.items():

    if not re.match(r"B02001_00[2-9]E", census_code):
        continue

    print(f"creating map for {census_code}: {description}")
    gis.make_map(
        shapefile_dir,
        valid_data,
        join_on="ZCTA5CE10",
        include=variables,
        color_by=f"% {description}",
        save_to=here / f"tx-zcta-map-{census_code}.html",
        trim=True,  # We definitely don't want all us zip codes on this map
    )
