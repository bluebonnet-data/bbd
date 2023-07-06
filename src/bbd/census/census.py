from __future__ import annotations
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, OrderedDict
from bbd.census.census_table import CensusTable
from bbd.models import geography
import urllib.parse
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
pd.set_option('display.max_columns', None)

@dataclass
class Census:
    api_key: str
    geography_values: OrderedDict[geography.Geography, str]
    year: str | int
    dataset: dataset.Dataset
    results: list[str] = field(default_factory = list) # list of CensusResult objects
    available_variables: pd.DataFrame = field(default_factory = pd.DataFrame) # dataframe of all available variables
    census_tables: list[CensusTable] = field(default_factory = list) # a list of CensusTable objects

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
            if i < statement_count:
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
        if len(self.census_tables) == 0:
            url = f"https://api.census.gov/data/{self.year}/{self.dataset.value}/variables.json"
            variable_data = requests.get(url)
            json = variable_data.json()
            attribute_names = [item for item in json["variables"]]
            names_to_tables = {}
            for item in attribute_names:
                one_attribute = json["variables"][item]
                if "concept" in one_attribute and "label" in one_attribute and "group" in one_attribute:
                    label = one_attribute["label"]
                    concept = one_attribute["concept"]
                    group = one_attribute["group"]
                    if group not in names_to_tables:
                        names_to_tables[group] = CensusTable(variable_id = group,
                                                             variable_description = concept,
                                                             attributes = [(item, label)])
                    else:
                        names_to_tables[group].attributes.append((item, label))
            self.census_tables = names_to_tables
        return self.census_tables

    def search_variables(self, search_string: str, number_of_results: int):
        names_to_tables = self._get_all_vars()
        df = pd.DataFrame()
        df["variable_id"] = [item.variable_id for item in names_to_tables.values()]
        df["variable_description"] = [item.variable_description for item in names_to_tables.values()]
        df["attributes"] = [item.attributes for item in names_to_tables.values()]
        df["attribute_names"] = df["attributes"].apply(lambda x: [item[0] for item in x])

        proportion_matches = df["variable_description"].apply(lambda x: self._proportion_match(search_string, x))
        df["match_proportion"] = proportion_matches
        df = df[["variable_id", "variable_description", "attribute_names", "match_proportion"]]
        return df.sort_values(by = "match_proportion", ascending = False).head(number_of_results)


class CensusResult():
    def __init__(self, response: requests.Reponse, variables: list[str]):
        self.response = response
        self.variables = variables
        self.data = response.json()

