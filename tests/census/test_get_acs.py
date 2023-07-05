from bbd import census, models


def _construct_call(variables):
    census.api_key.key = "MyApiKey"

    return census.construct_api_call(
        geography=models.Geography.STATE,
        variables=variables,
        year=2018,
        dataset=census.DataSet.ACS5_DETAIL,
    )


def test_single_variable():
    call = _construct_call("B03003_001E")

    assert (
        call
        == "https://api.census.gov/data/2018/acs/acs5?get=B03003_001E&for=state:*&key=MyApiKey"
    )


def test_multiple_variables():
    call = _construct_call("B03003_001E,NAME")

    assert (
        call
        == "https://api.census.gov/data/2018/acs/acs5?get=B03003_001E,NAME&for=state:*&key=MyApiKey"
    )


def test_multiple_variable_list():
    call = _construct_call(["B03003_001E", "NAME"])

    assert (
        call
        == "https://api.census.gov/data/2018/acs/acs5?get=B03003_001E,NAME&for=state:*&key=MyApiKey"
    )


def test_single_variable_list():
    call = _construct_call(["B03003_001E"])

    assert (
        call
        == "https://api.census.gov/data/2018/acs/acs5?get=B03003_001E&for=state:*&key=MyApiKey"
    )
