from bbd import census


census.api_key.key = ""


def test_call():
    geography = census.Geography.STATE
    variables = "B03003_001E"
    year = 2018
    dataset = census.DataSets.ACS5_DETAIL

    call = census.get_acs(geography, variables, year, dataset)

    return call


if __name__ == "__main__":
    test_call()
