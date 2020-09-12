from typing import Union, List

from .geography import Geography
from .datasets import DataSets


def get_acs(
    geography: Geography,
    variables: Union[str, List[str]],
    year: Union[str, int] = 2018,
    dataset: DataSets = DataSets.ACS5_DETAIL,
):
    """Get census acs data"""

    # Convert input year to string
    year = str(year)

    if isinstance(variables, list):
        variables = ",".join(variables)
