from bbd.census import Census, DataSet
from bbd.models import Geography
from config import API_KEY
from collections import OrderedDict

def test_typical_usage():
    key = 'abc123'
    cen = Census(key, ...)

    res : CensusResult = cen.get_acs(state='NY', county="Nassau")

def test_create_census():
    api_key = API_KEY
    geography = Geography.SUBDIVISION
    year = 2018
    dataset = DataSet.ACS1
    census = Census(api_key = api_key, geography = geography, year = year, dataset = dataset)

def test_build_url():
    api_key = "YOUR_KEY_GOES_HERE"
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    goal_url = "https://api.census.gov/data/2019/acs/acs1?get=NAME,B01001_001E&for=state:36&for=county:*&for=county%20subdivision:*&key=YOUR_KEY_GOES_HERE"
    test_url = census._build_url(variables)
    print(test_url)
    assert goal_url == test_url

def test_make_query():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["B01001_001E"]
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    result = census._make_query(variables)
    print(result.json())
    assert result is not None