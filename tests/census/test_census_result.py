from __future__ import annotations
from bbd.census import Census, DataSet
from bbd.models import Geography
from config import API_KEY
from bbd.census.geography_unit import GeographyUnit
from bbd.census.arguments import Arguments


# Make a sensible dataframe with the lowest level being "subdivision" for all in NY only
def test_dataframe_county_leaf():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographyUnit(argument=Arguments.in_input, label=Geography.STATE, value="36")
    county = GeographyUnit(argument=Arguments.in_input, label=Geography.COUNTY, value="*")
    subdivision = GeographyUnit(argument=Arguments.for_input, label=Geography.COUNTY_SUBDIVISION, value=None)
    geography_units = [subdivision, state, county]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    result = census.get_data(variables)
    print(result.dataframe)


# Make a sensible dataframe with the lowest level being "county" for all in NY only
def test_dataframe_subdivision_leaf():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographyUnit(argument=Arguments.in_input, label=Geography.STATE, value="36")
    county = GeographyUnit(argument=Arguments.for_input, label=Geography.COUNTY, value= "*")
    geography_units = [state, county]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    result = census.get_data(variables)
    print(result.dataframe)

# get a sensible dataframe in state, for school district
def test_dataframe_state_school_district():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    school = GeographyUnit(argument=Arguments.for_input, label=Geography.SCHOOL_DISTRICT_UNIFIED, value="*")
    state = GeographyUnit(argument=Arguments.in_input, label=Geography.STATE, value= "04")
    geography_units = [school, state]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    result = census.get_data(variables)
    print(result.dataframe)

def test_dataframe_metro_stat_area_leaf():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    principal_city_or_part = GeographyUnit(argument=Arguments.for_input, label=Geography.PRINCIPAL_CITY_OR_PART, value= "*")
    metro_stat_area = GeographyUnit(argument=Arguments.in_input, label=Geography.METROPOLITAN_MICROPOLITAN_STATISTICAL_AREA, value="19820")
    state_or_part =  GeographyUnit(argument=Arguments.none_input, label=Geography.STATE_OR_PART, value= "26")
    geography_units = [principal_city_or_part, metro_stat_area, state_or_part]
    census = Census(api_key=api_key, geography_units=geography_units, year=year, dataset=dataset)
    url = census._build_url(input_strings = variables)
    print(url)
    result = census.get_data(variables)

    print(result.dataframe)