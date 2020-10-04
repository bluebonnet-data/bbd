import re
from typing import Union, List

import requests

from ..working_directory import working_directory

from .geography import Geography
from .datasets import DataSets
from .api_key import api_key
from .load import load_json_str, load_json_file
from .us import state_to_fips


def get_acs(
    geography: Geography,
    variables: Union[str, List[str]],
    year: Union[str, int] = 2018,
    dataset: DataSets = DataSets.ACS5_DETAIL,
    state: Union[str, None] = None,
    county: Union[str, None] = None,
    cache: bool = False,
):
    """Get census acs data"""
    call = construct_api_call(geography, variables, year, dataset, state, county)

    save_file = working_directory.resolve(url_to_filename(call)).with_suffix(".json")

    if cache is True and save_file.exists() and save_file.is_file():
        return load_json_file(save_file)

    r = requests.get(call, stream=True)
    if not r.ok:
        raise ValueError(
            "Bad request. "
            f"Status code: {r.status_code}; Call: {call}; Content: {r.content}"
        )

    if "<html>" in r.text:
        raise ValueError(
            f"Census API returned html response -- expected json. Response: {r.text}"
        )

    content = load_json_str(r.content)

    if cache is True:
        with open(save_file, "w") as f:
            f.write(r.text)

    return content


def url_to_filename(url: str) -> str:
    """Converts url to a filename by removing invalid filename characters

    Note that this will not always work since windows has very particular file
    naming rules.
    """

    # Replace "*", used as geography wildcard, with "all"
    url = url.replace("*", "all")

    # Remove the beginning of the call since it is always the same
    url = url.replace("https://api.census.gov/data/", "")

    # Remove the api key if present
    key_index = url.find("key")
    if key_index != -1:
        url = url[:key_index]

    # Only keep letters, numbers, or _, ., -
    return "".join(re.findall("[a-zA-Z0-9_.-]*", url))


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
        in_state = f"&in=state:{state_to_fips(state)}"
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
