from bbd.census import Census
from bbd.census.geographic_unit import GeographicUnit
# HOW TO CREATE A CENSUS OBJECT FOR PERFORMING API PULLS
# 1. Save the API key securely to a variable
# 2. Create GeographyUnit objects
# 3. Create the object

###########################
# Import API key from file
###########################
api_key_file = Path(__file__).parent.absolute() / "census_api_key.txt"
with open(api_key_file, "r") as f:
    API_KEY = f.readlines()[0]

##############################
# Create GeographyUnit Objects
##############################
# First, decide on the unit of analysis your final dataset will have.
# This will determine the setup for your GeographyUnit objects
# GeographyUnits take in two arguments: a geography, and an analysis level
# the analysis level indicates whether you want data "for" all locations of this type,
# or if this geography represents the top-level; the place you want to find data "in". You can also
# use "none_level" for api-pulls which require unorthodox arguments, which we will discuss in a future guide.

# Example: geographic units targeting data for all counties in the state of New York (36 = Census code for New York)
county = GeographicUnit(analysis_level=AnalysisLevel.for_level, geography=Geography.COUNTY, value="*")
state = GeographicUnit(analysis_level=AnalysisLevel.in_level, geography=Geography.STATE, value="36")
geographic_units = [state, county]

########################
# Create a Census Object
########################
# Specify the year and dataset you want.
year = 2019
dataset = DataSet.ACS1
# Create the census object.
census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)