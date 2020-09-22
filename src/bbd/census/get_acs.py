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

    # Ensure input year is string
    year = str(year)

    # If variables are passed in as a list ["a", "b", ...] then join them: "a,b,..."
    if isinstance(variables, list):
        variables = ",".join(variables)
