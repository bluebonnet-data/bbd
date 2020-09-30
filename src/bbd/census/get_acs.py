from typing import Union, List

from .geography import Geography
from .datasets import DataSets
from .api_key import api_key


def get_acs(
    geography: Geography,
    variables: Union[str, List[str]],
    year: Union[str, int] = 2018,
    dataset: DataSets = DataSets.ACS5_DETAIL,
    state: Union[str, None] = None,
    county: Union[str, None] = None,
):
    """Get census acs data"""
    call = construct_api_call(geography, variables, year, dataset, state, county)

    # TODO return the call's contents
    return call


def construct_api_call(
    geography: Geography,
    variables: Union[str, List[str]],
    year: Union[str, int] = 2018,
    dataset: DataSets = DataSets.ACS5_DETAIL,
    state: Union[str, None] = None,
    county: Union[str, None] = None,
):
    """Construct a url call to the census api"""

    # If variables are passed in as a list ["a", "b", ...] then join them: "a,b,..."
    if isinstance(variables, list):
        variables = ",".join(variables)

    # Format the geography for the API call
    for_geography = f"&for={geography}:*"

    # If a state is provided, request the data returned be within it
    if state is not None:
        in_state = f"&in=state:{state}"
    else:
        in_state = ""

    # If a county is provided, request the data returned be within it
    if county is not None:
        in_county = f"&in=county:{county}"
    else:
        in_county = ""

    # Census api call
    return (
        f"https://api.census.gov/data/{year}/{dataset}"
        f"?get={variables}{for_geography}{in_state}{in_county}"
        f"&key={api_key.key}"
    )
