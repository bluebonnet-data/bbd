from __future__ import annotations
from bbd.census import Census, DataSet
from bbd.models import GEOGRAPHY
from config import API_KEY
from bbd.census.geographic_unit import GeographicUnit
from bbd.census.enumerations.analysis_level import AnalysisLevel


# Make a sensible dataframe with the lowest level being "subdivision" for all in NY only
def test_dataframe_county_leaf():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census.get_data(variables)
    assert len(result.dataframe) > 0
    print(result.dataframe)


# Make a sensible dataframe with the lowest level being "county" for all in NY only
def test_dataframe_subdivision_leaf():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY, value="*")
    geographic_units = [state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census.get_data(variables)
    assert len(result.dataframe) > 0
    print(result.dataframe)

# get a sensible dataframe in state, for school district
def test_dataframe_state_school_district():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    school = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.SCHOOL_DISTRICT_UNIFIED, value="*")
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="04")
    geographic_units = [school, state]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census.get_data(variables)
    assert len(result.dataframe) > 0
    print(result.dataframe)

# Get a sensible dataframe in state, for metro/micropolitain statistical area
def test_dataframe_metro_stat_area_leaf():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    principal_city_or_part = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.PRINCIPAL_CITY_OR_PART, value="*")
    metro_stat_area = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.METROPOLITAN_MICROPOLITAN_STATISTICAL_AREA, value="19820")
    state_or_part = GeographicUnit(analysis_level=AnalysisLevel.NONE, geography=GEOGRAPHY.STATE_OR_PART, value="26")
    geographic_units = [principal_city_or_part, metro_stat_area, state_or_part]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census.get_data(variables = variables)
    assert len(result.dataframe) > 0
    print(result.dataframe)

def test_census_acs5_tract():
    api_key = API_KEY
    year = 2020
    dataset = DataSet.ACS5
    variables = ["NAME", "B01001_001E"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.TRACT,
                                 value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census.get_data(variables = variables)
    print(result.dataframe)
    assert len(result.dataframe) > 0


