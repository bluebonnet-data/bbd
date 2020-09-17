import json


def extract_from_json(fp, headers: list) -> dict:
    """Extract column data for the requested headers"""

    with open(fp, "r") as f:
        data = json.load(f)

    # Top row is header row
    all_headers = data[0]

    # Get indexes for each requested header
    indexes = [all_headers.index(h) for h in headers]

    # Construct data container
    d = {h: [] for h in headers}

    # Pull out the requested data in each row
    for row in data[1:]:  # Skip header row

        [d[h].append(row[i]) for h, i in zip(headers, indexes)]

    return d
