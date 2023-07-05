from __future__ import annotations

import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, OrderedDict
# from collections import OrderedDict
from bbd.models import geography
import urllib.parse
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class Census:
    api_key: str
    geography_values: OrderedDict[geography.Geography, str]
    year: str | int
    dataset: dataset.Dataset
    results: list[str] = field(default_factory = list)
    available_variables: pd.DataFrame = field(default_factory = pd.DataFrame)

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
        response = requests.get(url)
        return response



    def get_acs(self, variables) -> CensusResult:
        '''Query the database '''
        response = self._make_query(variables)
        result = CensusResult(response=response, variables=variables)
        self.results.append(result)
        return result

    def _proportion_match(self, search_string: str, match_string:str):
        search_string = search_string.lower()
        match_string = match_string.lower()
        cv = CountVectorizer()
        count_matrix = cv.fit_transform([search_string, match_string])
        proportion_match = cosine_similarity(count_matrix)[0][1]
        return proportion_match

    def _get_all_vars(self):
        if len(self.available_variables) == 0:
            url = f"https://api.census.gov/data/{self.year}/{self.dataset.value}/variables.json"
            variable_data = requests.get(url)
            json = variable_data.json()
            irrelevant_variables = ["for", "in", "ucgid"]
            variables = [item for item in json["variables"] ]
            concepts_to_attributes = {}
            for item in variables:
              one_variable = json["variables"][item]
              label = one_variable["label"]
              if "concept" in one_variable:
                concept = one_variable["concept"]
                labeled_variable = (item, label)
                if concept not in concepts_to_attributes:
                  concepts_to_attributes[concept] = [labeled_variable]
                else:
                  concepts_to_attributes[concept].append(labeled_variable)
            concepts_column = concepts_to_attributes.keys()
            attributes_column = concepts_to_attributes.values()
            df = pd.DataFrame()
            df["concept"] = concepts_column
            df["attributes"] = attributes_column
            df["attribute_names"] = df["attributes"].apply(lambda x: [item[0] for item in x])
            self.available_variables = df
        return self.available_variables

    def explore(self, search_string: str, number_of_results: int):
        df = self._get_all_vars()
        proportion_matches = df["concept"].apply(lambda x: self._proportion_match(search_string, x))
        df["match_proportion"] = proportion_matches
        df = df[["concept", "match_proportion", "attribute_names"]]
        return df.sort_values(by = "match_proportion", ascending = False).head(number_of_results)



class CensusResult():
    def __init__(self, response: requests.Reponse, variables: list[str]):
        self.response = response
        self.variables = variables
        self.data = response.json()

