from pathlib import Path
from pprint import pprint

from bbd import census

# For convenience and security so people don't go accidentally commiting their census
# api keys, just store it as the first line of a file named # `census_api_key.txt`
# in the same directory as this file and it will be read in automatically.
api_key_file = Path(__file__).parent.absolute() / "census_api_key.txt"
with open(api_key_file, "r") as f:
    census.api_key.key = f.readlines()[0]

data = census.get_acs(
    geography=census.Geography.STATE,
    variables="NAME,B03003_001E",
    year=2018,
    dataset=census.DataSet.ACS5_DETAIL,
)

pprint(data)
