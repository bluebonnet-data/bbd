from bbd.census import Census

# HOW TO FIND THE CENSUS CODES FOR THE VARIABLES AND GROUPS YOU WANT TO EXAMINE
#Create a census object (see instructions in create_census_example.py)

api_key_file = Path(__file__).parent.absolute() / "census_api_key.txt"
with open(api_key_file, "r") as f:
    API_KEY = f.readlines()[0]

county = GeographicUnit(analysis_level=AnalysisLevel.for_level, geography=Geography.COUNTY, value="*")
state = GeographicUnit(analysis_level=AnalysisLevel.in_level, geography=Geography.STATE, value="36")
geographic_units = [state, county]
year = 2019
dataset = DataSet.ACS1
census = Census(api_key=API_KEY, geographic_units=geographic_units, year=year, dataset=dataset)

# Get a dataframe of all available variables in no particular order.
df = census.search_variables()
print(df)

# Get a dataframe of all available variables sorted by similarity of description to a given search string.
search_string = "female household"
df = census.search_variables(search_string = search_string)
print(df)

# Get a dataframe of variables sorted by similarity to a search string, limiting the number of results.
search_string = "housing cost"
number_of_results = 10
df = census.search_variables(search_string = search_string, number_of_results = number_of_results)
print(df)
