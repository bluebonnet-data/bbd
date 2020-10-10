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
shapefile_dir = census.get_shapefile(
    geography=census.Geography.ZCTA,
    state="tx",
    year=2018,
    cache=True,
)

# We only want specific zctas
with open(here / "tx_harris_county_zctas.txt", "r") as f:
    valid_zctas = [line.rstrip() for line in f.readlines()]

valid_zctas_indexes = [i for i, name in enumerate(data["NAME"]) if name in valid_zctas]

valid_data = {}
for variable, value_list in data.items():
    valid_data[variable] = [value_list[i] for i in valid_zctas_indexes]

# Print out the race data for the valid zip codes
with open(here / "data_for_team.csv", "w") as f:
    for header in valid_data.keys():
        f.write(f"{header}\t")
    f.write("\n")
    for i in range(len(valid_data["NAME"])):
        [f.write(f"{valid_data[key][i]}\t") for key in valid_data.keys()]
        f.write("\n")

# Make entry with just the proper zcta name to play nicely with the shapefile
valid_data["ZCTA5CE10"] = valid_data["zip code tabulation area"]

# Percentage of black or african american people out of the total respondants (to color by)
valid_data["% Black or African American"] = [
    float(black) / float(tot) * 100 if not tot == "0" else None
    for tot, black in zip(valid_data["B02001_001E"], valid_data["B02001_003E"])
]
variables["% Black or African American"] = "% Black or African American"

# Make the map!
gis.make_map(
    shapefile_dir,
    valid_data,
    join_on="ZCTA5CE10",
    include=variables,
    color_by="% Black or African American",
    save_to=here / "tx-zcta-map.html",
    trim=True,
)
