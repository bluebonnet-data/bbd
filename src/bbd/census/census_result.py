from __future__ import annotations
import requests
import pandas as pd

class CensusResult():
    def __init__(self, response: requests.Reponse, variables: list[str]):
        self.response = response
        self.variables = variables
        self.data = response.json()

        # Create pandas dataframe of result Json
        json = self.data
        for i in range(len(json)):
            if i == 0:
                df = pd.DataFrame(columns=json[i])
            else:
                df.loc[i] = json[i]

        self.dataframe = df
