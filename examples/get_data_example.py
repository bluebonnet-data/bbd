

# HOW TO PULL ACS DATA FROM A CENSUS OBJECT
# 1. Create a census object (see create_census_example.py for instructions)
# 2. Pull the data, as shown below

#Create a census object (see instructions in create_census_example.py)
api_key_file = Path(__file__).parent.absolute() / "census_api_key.txt"
with open(api_key_file, "r") as f:
    API_KEY = f.readlines()[0]

county = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=Geography.COUNTY, value="*")
state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=Geography.STATE, value="36")
geographic_units = [state, county]
year = 2019
dataset = DataSet.ACS1
census = Census(api_key=API_KEY, geographic_units=geographic_units, year=year, dataset=dataset)


###############
# Pull the data
###############
# Specify any census variables you want.
variables = ["NAME", "B01001_001E"]
# Specify any census groups you want; results will include all variables belonging to that group.
groups = ["B02015"]
# pull the data for those variables
result = census.get_data(variables = variables, groups = groups)
# The result will also be stored in census.results, which is a list of CensusResult objects created during this session.
# Get the dataframe out of the result object.
df = result.dataframe
print(df.head())

