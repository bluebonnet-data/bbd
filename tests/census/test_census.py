from bbd.census import Census, DataSet
from bbd.models import Geography
from config import API_KEY
from collections import OrderedDict

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
    variables = ["NAME", "B01001_001E"]
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    result = census._make_query(variables)
    print(result.json())
    assert result is not None

def test_get_census_result():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    result = census.get_acs(variables)
    print(f"result json: {result.data}")
    assert result.data is not None

def test_get_all_vars():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    names_to_tables = census._get_all_vars()
    assert len(names_to_tables) > 50

def test_proportion_match():
    search_string = "this is the first string"
    comparison_string = "AND THIS, MY FRIEND, IS THE SECOND STRING"
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    match_proportion = census._proportion_match(search_string, comparison_string)
    print(match_proportion)
    assert match_proportion > 0.50


def test_census_search_variables():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    search_string = "sex by occupation of workers"
    number_of_results = 10
    df = census.search_variables(search_string, number_of_results)
    assert len(df) > 0
    assert len(df["match_proportion"]) > 0
    assert len(df.columns) == 4
    print(df)
