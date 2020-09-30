from bbd import census


census.api_key.key = "MyApiKey"


def test_call():
    geography = census.Geography.STATE
    variables = "B03003_001E"
    year = 2018
    dataset = census.DataSets.ACS5_DETAIL

    call = census.construct_api_call(geography, variables, year, dataset)

    assert (
        call
        == "https://api.census.gov/data/2018/acs/acs5?get=B03003_001E&for=state:*&key=MyApiKey"
    )


if __name__ == "__main__":
    test_call()
