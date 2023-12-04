from bbd.census import Census, DataSet
from bbd.models import GEOGRAPHY
from config import API_KEY
from bbd.census.geographic_unit import GeographicUnit
from bbd.census.enumerations.analysis_level import AnalysisLevel


def test_build_url_no_nones():
    api_key = "YOUR_KEY_GOES_HERE"
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography = GEOGRAPHY.STATE, value ="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography = GEOGRAPHY.COUNTY, value ="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography = GEOGRAPHY.COUNTY_SUBDIVISION, value ="*")
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    goal_url = "https://api.census.gov/data/2019/acs/acs1?get=NAME,B01001_001E&for=county%20subdivision:*&in=state:36&in=county:*&key=YOUR_KEY_GOES_HERE"
    test_url = census._build_url(variables_groups= variables)
    print(test_url)
    assert goal_url == test_url



def test_make_query_no_nones():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value="*")
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census._make_query(variables = variables, groups = None)
    print(result.json())
    assert result is not None

def test_make_query_has_nones():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census._make_query(variables)
    print(result.json())
    assert result is not None

def test_make_query_has_groups():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    groups = ["B02015"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    result = census._make_query(variables = variables, groups = groups)
    print(result.json())
    assert result is not None

def test_get_data_has_groups():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    county = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY, value="*")
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    geographic_units = [state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    variables = ["NAME", "B01001_001E"]
    groups = ["B02015"]
    result = census.get_data(variables=variables, groups=groups)
    df = result.dataframe
    assert len(df) > 0
    print(df.head())

def test_get_all_vars():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    variables = ["NAME", "B01001_001E"]
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
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
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    match_proportion = census._proportion_match(search_string, comparison_string)
    print(match_proportion)
    assert match_proportion > 0.50

def test_dataframe_all_variables():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    df = census._datafame_all_variables()
    print(df)
    assert df is not None

def test_census_search_variables():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
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
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION, value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    df = census.search_variables(search_string = None, number_of_results = 30)
    assert len(df) > 0
    print(df)

def test_census_search_variables_no_n():
    api_key = API_KEY
    year = 2019
    dataset = DataSet.ACS1
    state = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.STATE, value="36")
    county = GeographicUnit(analysis_level=AnalysisLevel.IN, geography=GEOGRAPHY.COUNTY, value="*")
    subdivision = GeographicUnit(analysis_level=AnalysisLevel.FOR, geography=GEOGRAPHY.COUNTY_SUBDIVISION,
                                 value=None)
    geographic_units = [subdivision, state, county]
    census = Census(api_key=api_key, geographic_units=geographic_units, year=year, dataset=dataset)
    df = census.search_variables()
    assert len(df) > 0
    print(df)



    # state: 36
    # county: *
    # subdivision: *
    # data for each subdivision for each county in new york

    # state: 36
    # county: None
    # subdivision: *
    # Query not permitted

    # state: 36
    # county: *
    # subdivision: None
    # Query not permitted
