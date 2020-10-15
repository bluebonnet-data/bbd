"""Some potentially useful functions for processing OpenFEC data after it has
been downloaded by get_fec. Definitely more could be added here, these are
just examples."""

from collections import Counter

from .get_fec import get_fec

def fec_counter(
    fec_data: dict,
    metric: str
):
    """Returns a Counter that states how many instances of each unique value
    of metric are found in the results of fec_data."""

    # Error if there is no "results" section
    if not "results" in fec_data:
        raise ValueError(
            "fec_data must include a value with name 'results'"
        )

    # List of the values taken by "metric"
    vals = [result[metric] for result in fec_data["results"]]
    return Counter(vals)

def get_next_page(
    fec_data: dict,
    endpoint: str,
    params: dict
):
    """Gets the next page based on fec_data's pagination section and the given
    endpoint and params. This is kind of redundant and there's probably a better
    way to do this."""

    # Error if there is no "pagination" section
    if not "pagination" in fec_data:
        raise ValueError(
            "fec_data must include a value with name 'pagination'"
        )

    # Error if there is no "last_indexes"
    if not "last_indexes" in fec_data["pagination"]:
        raise ValueError(
            "fec_data's 'pagination' object must include a value with name 'last_indexes'"
        )

    # Error if "last_indexes" is not a dict
    if not isinstance(fec_data["pagination"]["last_indexes"], dict):
        raise ValueError(
            "No 'last_indexes' available. This probably means you are already on the last page."
        )

    # Get the next page
    last_indexes = fec_data["pagination"]["last_indexes"]
    return get_fec(endpoint, {**params, **last_indexes})
