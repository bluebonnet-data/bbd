from pathlib import Path
from pprint import pprint

from bbd import census

# For convenience and security so people don't go accidentally commiting their
# census api keys, just store it as the first line of a file named
# user/census_api_key.txt and this example will read it in automatically.
api_key_file = Path(__file__).parent.parent / "user/census_api_key.txt"
with open(api_key_file, "r") as f:
    census.api_key.key = f.readlines()[0]

geography = census.Geography.STATE
variables = "B03003_001E"
year = 2018
dataset = census.DataSets.ACS5_DETAIL

data = census.get_acs(geography, variables, year, dataset)

pprint(data)
