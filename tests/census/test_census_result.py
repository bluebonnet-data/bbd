from __future__ import annotations
from bbd.census import Census, DataSet
from bbd.models import Geography
from config import API_KEY
from bbd.census.geography_unit import GeographyUnit
from bbd.census.arguments import Arguments


# Make a sensible dataframe with the lowest level being "subdivision"
def test_dataframe_subdivision_leaf():
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