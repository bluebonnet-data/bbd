from bbd.census import Census, DataSet
from bbd.models import Geography
from config import API_KEY
from collections import OrderedDict

#Set up census object to use on all tests
api_key = API_KEY
year = 2019
dataset = DataSet.ACS1
variables = ["NAME", "B01001_001E"]
geography_values = OrderedDict()
geography_values[Geography.STATE] = "36"
geography_values[Geography.COUNTY] = "*"
geography_values[Geography.COUNTY_SUBDIVISION] = "*"
census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)