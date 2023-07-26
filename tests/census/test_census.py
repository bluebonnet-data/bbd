from bbd.census import Census, DataSet
from bbd.models import Geography
from config import API_KEY
from collections import OrderedDict
from bbd.census.geography_unit import GeographyUnit
from bbd.census.arguments import Arguments


def test_build_url_no_nones():
    api_key = "YOUR_KEY_GOES_HERE"
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographyUnit(argument=Arguments.in_input, label = Geography.STATE, value = "36")
    county = GeographyUnit(argument=Arguments.in_input,label = Geography.COUNTY, value = "*")
    subdivision = GeographyUnit(argument=Arguments.for_input,label = Geography.COUNTY_SUBDIVISION, value = "*")
    geography_units = [subdivision, state, county]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    goal_url = "https://api.census.gov/data/2019/acs/acs1?get=NAME,B01001_001E&for=county%20subdivision:*&in=state:36&in=county:*&key=YOUR_KEY_GOES_HERE"
    test_url = census._build_url(variables)
    print(test_url)
    assert goal_url == test_url



def test_make_query_no_nones():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographyUnit(argument=Arguments.in_input, label=Geography.STATE, value="36")
    county = GeographyUnit(argument=Arguments.in_input, label=Geography.COUNTY, value="*")
    subdivision = GeographyUnit(argument=Arguments.for_input, label=Geography.COUNTY_SUBDIVISION, value="*")
    geography_units = [subdivision, state, county]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    result = census._make_query(variables = variables, groups = None)
    print(result.json())
    assert result is not None

def test_make_query_has_nones():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographyUnit(argument=Arguments.in_input, label=Geography.STATE, value="36")
    county = GeographyUnit(argument=Arguments.in_input, label=Geography.COUNTY, value="*")
    subdivision = GeographyUnit(argument=Arguments.for_input, label=Geography.COUNTY_SUBDIVISION, value=None)
    geography_units = [subdivision, state, county]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    result = census._make_query(variables)
    print(result.json())
    assert result is not None

def test_make_query_has_groups():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    groups = ["B02015"]
    state = GeographyUnit(argument=Arguments.in_input, label=Geography.STATE, value="36")
    county = GeographyUnit(argument=Arguments.in_input, label=Geography.COUNTY, value="*")
    subdivision = GeographyUnit(argument=Arguments.for_input, label=Geography.COUNTY_SUBDIVISION, value=None)
    geography_units = [subdivision, state, county]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    result = census._make_query(variables = variables, groups = groups)
    print(result.json())
    assert result is not None

#Can we get a sensus result with all nested state counties
def test_get_census_result_all_counties():
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

#Can we get a sensus result with only One state's results
def test_get_census_result_no_counties():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = None
    geography_values[Geography.COUNTY_SUBDIVISION] = None
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
    print(names_to_tables)
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

def test_dataframe_all_variables():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    df = census._datafame_all_variables()
    print(df)
    assert df is not None

def test_census_search_variables():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    search_string = "county"
    number_of_results = 10
    df = census.search_variables(search_string, number_of_results)
    assert len(df) > 0
    assert len(df["match_proportion"]) > 0
    assert len(df.columns) == 4
    print(df)

def test_census_search_variables_no_string():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    df = census.search_variables(search_string = None, number_of_results = 30)
    assert len(df) > 0
    print(df)

def test_acs_to_df():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    geography_values = OrderedDict()
    geography_values[Geography.STATE] = "36"
    geography_values[Geography.COUNTY] = "*"
    geography_values[Geography.COUNTY_SUBDIVISION] = "*"
    variables = ["NAME", "B01001_001E"]
    census = Census(api_key=api_key, geography_values=geography_values, year=year, dataset=dataset)
    result = census.get_acs(variables)
    print(result.data)
