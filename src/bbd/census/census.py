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
from bbd.census.census_result import CensusResult
from bbd.census import geography_unit

# Make pandas display properly; consider removing later
pd.set_option('display.max_columns', None)



@dataclass
class Census:
    api_key: str
    geography_units: list[geography_unit.GeographyUnit]
    year: str | int
    dataset: dataset.Dataset
    results: list[str] = field(default_factory = list) # list of CensusResult objects
    available_variables: pd.DataFrame = field(default_factory = pd.DataFrame) # dataframe of all available variables
    census_tables: list[CensusTable] = field(default_factory = list) # a list of CensusTable objects

    def _build_url(self, input_strings: list[str]):
        base_url = "https://api.census.gov/data"
        # Collect all parts
        year = self.year
        dataset = self.dataset.value
        input_strings = ",".join(input_strings)
        key = self.api_key
        geo_url = ""

        # parse geography
        geographies = self.geography_units
        for unit in geographies:
            argument = unit.argument.value
            label = urllib.parse.quote(unit.label.value, safe = "()/")
            value = unit.value
            if value is None:
                geo_url += f"{argument}{label}"
            else:
                geo_url += f"{argument}{label}:{value}"
        full_url = f"{base_url}/{year}/{dataset}?get={input_strings}{geo_url}&key={key}"
        return full_url


    def _make_query(self, variables: Optional[str] = None, groups: Optional[str] = None):
        assert variables or groups
        input_strings = [item for item in variables if variables is not None]
        if groups is not None:
            for group in groups:
                group_string = f"group({group})"
                input_strings.append(group_string)
        url = self._build_url(input_strings)
        response = requests.get(url)
        return response

    def get_data(self, variables) -> CensusResult:
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

    def _datafame_all_variables(self):
        if len(self.available_variables) == 0:
            names_to_tables = self._get_all_vars()
            df = pd.DataFrame()
            df["variable_id"] = [item.variable_id for item in names_to_tables.values()]
            df["variable_description"] = [item.variable_description for item in names_to_tables.values()]
            df["attributes"] = [item.attributes for item in names_to_tables.values()]
            df["attribute_names"] = df["attributes"].apply(lambda x: [item[0] for item in x])
            self.available_variables = df
        return self.available_variables

    def search_variables(self, search_string: Optional[str] = None, number_of_results: Optional[int] = None):
        df = self._datafame_all_variables()
        if search_string is not None:
            proportion_matches = df["variable_description"].apply(lambda x: self._proportion_match(search_string, x))
            df["match_proportion"] = proportion_matches
            df = df[["variable_id", "variable_description", "attribute_names", "match_proportion"]]
            df = df.sort_values(by="match_proportion", ascending=False).head(number_of_results)
        if number_of_results is not None:
            return df.head(number_of_results)
        else:
            return df.head()


