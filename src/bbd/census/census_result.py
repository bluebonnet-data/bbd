from __future__ import annotations
import requests


class CensusResult():
    def __init__(self, response: requests.Reponse, variables: list[str]):
        self.response = response
        self.variables = variables
        self.data = response.json()