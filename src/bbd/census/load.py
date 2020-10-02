import json


def load_json_file(fp, headers: list = None) -> dict:
    """Extract column data for the requested headers"""

    with open(fp, "r") as f:
        data = json.load(f)

    return organize(data, headers)


def load_json_str(s: str, headers: list = None) -> dict:
    """Extract column data for the requested headers"""

    data = json.loads(s)
    return organize(data, headers)


def organize(data: dict, headers: list = None) -> dict:
    """Extract column data for the requested headers"""

    # Top row is header row
    all_headers = data[0]

    # If there are no requested headers, get all of the data available.
    if headers is None:
        headers = all_headers

    # Get indexes for each requested header.
    indexes = [all_headers.index(h) for h in headers]

    # Construct data container
    d = {h: [] for h in headers}

    # Pull out the requested data in each row
    for row in data[1:]:  # Skip header row

        [d[h].append(row[i]) for h, i in zip(headers, indexes)]

    return d
