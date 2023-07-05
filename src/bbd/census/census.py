from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from typing import Optional, OrderedDict
# from collections import OrderedDict

from bbd.models import geography
import urllib.parse
import requests

@dataclass
class Census:
    api_key: str
    geography_values: OrderedDict[geography.Geography, str]
    year: str | int
    dataset: dataset.Dataset

    def _build_url(self, variables: list[str]):
        base_url = "https://api.census.gov/data"

        # Collect all parts
        year = self.year
        dataset = self.dataset.value
        variables = ",".join(variables)
        key = self.api_key

        # Parse the geography
        geo_statements = list(self.geography_values.items())
        statement_count = len(geo_statements)
        geo_url = ""
        for i in range(statement_count):
            if i <statement_count:
                prefix = "for"
            else:
                prefix = "in"
            geo_url = geo_url + (f"&{prefix}={urllib.parse.quote(geo_statements[i][0].value)}:{geo_statements[i][1]}")

        full_url = f"{base_url}/{year}/{dataset}?get={variables}{geo_url}&key={key}"
        return full_url


    def _make_query(self, variables):
        url = self._build_url(variables)
        result = requests.get(url)
        return result



    # def get_acs(self, variables: str | list[str], state = Optional[str] = None, county: Optional[str] = None) -> CensusResult
#       pass
#         '''Query the database '''
#         '''... do stuff ...'''
#
#         return CensusResult(self, data=data, variables=variables, state=state, county=county)
#
# @dataclass
# class CensusResult:
#     census: Census
#     variables: list[str]
#     data: pd.DataFrame
#     state: Optional[str] = None
#     county: Optional[str] = None
