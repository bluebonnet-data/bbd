"""A lot of the code here (as in the other files in this branch) is borrowed
from Noah's tool for census API calls. The main difference is that, given
the large number of endpoints in the OpenFEC API, the user needs to input their
chosen endpoint as a string and the parameters they have chosen as a dict."""

import json
import re
from urllib.parse import urlencode

from ..working_directory import working_directory

from .api_key import api_key

def get_fec(
    endpoint: str,
    params: dict,
    cache: bool = False
):
    """Get OpenFEC data. See https://api.open.fec.gov/developers for a list of
    endpoints and the parameters associated with each endpoint."""
    call = construct_api_call(endpoint, params)

    save_file = working_directory.resolve(url_to_filename(call)).with_suffix(".json")

    if cache is True and save_file.exists() and save_file.is_file():
        with open(save_file, "r") as f:
            return json.load(f)

    r = requests.get(call, stream=True)
    if not r.ok:
        raise ValueError(
            "Bad request. "
            f"Status code: {r.status_code}; Call: {call}; Content: {r.content}"
        )

    if "<html>" in r.text:
        raise ValueError(
            f"OpenFEC API returned html response -- expected json. Response: {r.text}"
        )

    content = json.loads(r.content)

    if cache is True:
        with open(save_file, "w") as f:
            f.write(r.text)

    return content

def url_to_filename(url: str) -> str:
    """Converts URL to filename."""

    # Remove the beginning of the call since it is always the same
    url = url.replace("https://api.open.fec.gov/v1/", "")

    # There may be slashes in the endpoint, replace with underscores for clarity
    url = url.replace("/", "_")

    # Remove the API key if present
    key_index = url.find("api_key")
    if key_index != -1:
        url = url[:key_index - 1]

    # Only keep letters, numbers, or _, ., -
    return "".join(re.findall("[a-zA-Z0-9_.-]*", url))

def construct_api_call(
    endpoint: str,
    params: dict
):
    """Construct a call to the OpenFEC API"""

    # Remove extra slashes from endpoint for greater input flexibility
    endpoint = endpoint.strip("/")

    # Format parameters
    url_params = urlencode(params)

    # Final API call
    return (
        "https://api.open.fec.gov/v1/"
        f"{endpoint}/?{url_params}"
        f"&api_key={api_key.key}"
    )
